from openai import OpenAI

from src.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)
from src.rag.context_builder import build_context
from src.rag.query_rewriter import rewrite_query
from src.retrieval.vector_search import semantic_hybrid_search


def create_chat_client() -> OpenAI:
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")

    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY is not configured")

    return OpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        base_url=f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/v1/",
    )


def answer_question(
    question: str,
    industry: str,
    department: str | None = None,
    classification: str | None = None,
    top_k: int = 3,
    conversation_history: list[dict] | None = None,
) -> dict:
    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not AZURE_OPENAI_CHAT_DEPLOYMENT:
        raise ValueError(
            "AZURE_OPENAI_CHAT_DEPLOYMENT is not configured"
        )

    # -----------------------------------------
    # 1. Rewrite conversational question
    # -----------------------------------------

    search_query = rewrite_query(
        question=question,
        conversation_history=conversation_history,
    )

    # -----------------------------------------
    # 2. Retrieve relevant knowledge
    # -----------------------------------------

    search_results = semantic_hybrid_search(
        query=search_query,
        top_k=top_k,
        industry=industry,
        department=department,
        classification=classification,
    )

    # -----------------------------------------
    # 3. Stop if retrieval returned nothing
    # -----------------------------------------

    if not search_results:
        return {
            "answer": (
                "I could not find sufficient information in the "
                "authorised knowledge base to answer this question."
            ),
            "sources": [],
            "search_query": search_query,
            "retrieval_trace": [],
        }

    # -----------------------------------------
    # 4. Build grounding context
    # -----------------------------------------

    context = build_context(search_results)

    # -----------------------------------------
    # 5. Prepare recent conversation context
    # -----------------------------------------

    history_text = ""

    if conversation_history:
        history_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in conversation_history
        )

    # -----------------------------------------
    # 6. Generate grounded answer
    # -----------------------------------------

    client = create_chat_client()

    response = client.responses.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        instructions="""
You are an enterprise knowledge assistant.

Answer the user's question using only the supplied knowledge-base context.

The conversation history is provided only to understand the conversational
context of the user's latest question. It must not be treated as an
authoritative source of enterprise information.

Rules:
- Use only the supplied knowledge-base context for factual claims.
- Do not use outside knowledge.
- Do not invent information.
- Do not treat previous assistant responses as authoritative evidence.
- If the knowledge-base context does not contain enough information, say so.
- Keep the answer concise and factual.
- Cite supporting sources using [SOURCE: filename, Page X] when page
  information is available.
- If page information is unavailable, cite using [SOURCE: filename].
""".strip(),
        input=f"""
CONVERSATION HISTORY:
{history_text or "No previous conversation."}

USER QUESTION:
{question}

SEARCH QUERY:
{search_query}

KNOWLEDGE BASE CONTEXT:
{context}
""".strip(),
    )

    # -----------------------------------------
    # 7. Build structured source list
    # -----------------------------------------

    sources = []

    for result in search_results:
        source = {
            "file_name": result["file_name"],
            "page_number": result.get("page_number"),
            "chunk_id": result["chunk_id"],
        }

        if source not in sources:
            sources.append(source)

    # -----------------------------------------
    # 8. Build retrieval diagnostic trace
    # -----------------------------------------

    retrieval_trace = []

    for result in search_results:
        retrieval_trace.append(
            {
                "chunk_id": result["chunk_id"],
                "file_name": result["file_name"],
                "page_number": result.get("page_number"),
                "search_score": result.get("score"),
                "reranker_score": result.get(
                    "reranker_score"
                ),
            }
        )

    # -----------------------------------------
    # 9. Return complete RAG result
    # -----------------------------------------

    return {
        "answer": response.output_text,
        "sources": sources,
        "search_query": search_query,
        "retrieval_trace": retrieval_trace,
    }