from src.rag.chat_service import RAGChatService


chat = RAGChatService(
    industry="it-support",
    department="service-desk",
    classification="internal",
)


question_1 = (
    "What is retrieval augmented generation?"
)

result_1 = chat.ask(question_1)

print("\nQUESTION 1")
print("=" * 60)
print(question_1)

print("\nSEARCH QUERY")
print(result_1["search_query"])

print("\nANSWER")
print(result_1["answer"])


question_2 = (
    "Why is it useful?"
)

result_2 = chat.ask(question_2)

print("\n\nQUESTION 2")
print("=" * 60)
print(question_2)

print("\nREWRITTEN SEARCH QUERY")
print(result_2["search_query"])

print("\nANSWER")
print(result_2["answer"])


print("\n\nSESSION HISTORY")
print("=" * 60)

for message in chat.session.get_history():
    print(
        f"{message['role']}: "
        f"{message['content']}"
    )
print("\nSESSION")
print(result_2["session_id"])

print("\nRETRIEVAL TRACE")

for item in result_2["retrieval_trace"]:
    print(
        f"Chunk: {item['chunk_id']} | "
        f"Search Score: {item['search_score']} | "
        f"Reranker Score: {item['reranker_score']}"
    )