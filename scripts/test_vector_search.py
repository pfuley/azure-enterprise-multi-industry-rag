from src.retrieval.vector_search import (
    hybrid_search,
    semantic_hybrid_search,
    vector_search,
)


query = "What is retrieval augmented generation?"


print("\nVECTOR SEARCH")
print("=" * 60)

vector_results = vector_search(
    query=query,
    industry="it-support",
    department="service-desk",
    classification="internal",
)

for result in vector_results:
    print("\nChunk:", result["chunk_id"])
    print("Score:", result["score"])
    print("Content:", result["content"])


print("\n\nHYBRID SEARCH")
print("=" * 60)

hybrid_results = hybrid_search(
    query=query,
    industry="it-support",
    department="service-desk",
    classification="internal",
)

for result in hybrid_results:
    print("\nChunk:", result["chunk_id"])
    print("Score:", result["score"])
    print("Content:", result["content"])


print("\n\nSEMANTIC HYBRID SEARCH")
print("=" * 60)

semantic_results = semantic_hybrid_search(
    query=query,
    industry="it-support",
    department="service-desk",
    classification="internal",
)

for result in semantic_results:
    print("\nChunk:", result["chunk_id"])
    print("Search Score:", result["score"])
    print("Reranker Score:", result["reranker_score"])
    print("Content:", result["content"])