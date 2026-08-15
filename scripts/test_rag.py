from src.rag.orchestrator import answer_question


question = "What is retrieval augmented generation?"

result = answer_question(
    question=question,
    industry="it-support",
    department="service-desk",
    classification="internal",
)

print("\nQUESTION")
print("=" * 60)
print(question)

print("\nANSWER")
print("=" * 60)
print(result["answer"])

print("\nSOURCES")
print("=" * 60)

for source in result["sources"]:
    print("-", source)