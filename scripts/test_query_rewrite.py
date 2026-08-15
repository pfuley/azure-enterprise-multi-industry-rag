from src.rag.orchestrator import answer_question


history = [
    {
        "role": "user",
        "content": "What is retrieval augmented generation?",
    },
    {
        "role": "assistant",
        "content": (
            "It retrieves external information before generating an answer."
        ),
    },
]

question = "Why is that useful?"

result = answer_question(
    question=question,
    industry="it-support",
    department="service-desk",
    classification="internal",
    conversation_history=history,
)

print("\nQUESTION")
print(question)

print("\nSEARCH QUERY")
print(result["search_query"])

print("\nANSWER")
print(result["answer"])

print("\nSOURCES")
for source in result["sources"]:
    print("-", source)