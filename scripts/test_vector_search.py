from src.retrieval.vector_search import (
    vector_search,
    hybrid_search,
)


query = "What is retrieval augmented generation?"


print("\nVECTOR SEARCH")
print("=" * 50)

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
print("=" * 50)

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