from src.retrieval.vector_search import semantic_hybrid_search
from src.security.authorization import AuthorizationContext


def evaluate_retrieval_case(
    test_case: dict,
    auth: AuthorizationContext,
    top_k: int = 3,
) -> dict:

    question = test_case["question"]
    expected_source = test_case["expected_source"]

    results = semantic_hybrid_search(
        query=question,
        top_k=top_k,
        auth=auth,
    )

    retrieved_sources = [
        result["file_name"]
        for result in results
    ]

    source_found = (
        expected_source
        in retrieved_sources
    )

    return {
        "id": test_case["id"],
        "question": question,
        "expected_source": expected_source,
        "retrieved_sources": retrieved_sources,
        "source_found": source_found,
        "top_k": top_k,
    }