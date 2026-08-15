from src.conversation.session import ConversationSession


session = ConversationSession(
    max_messages=4,
    summarize_count=2,
)

messages = [
    ("user", "What is RAG?"),
    (
        "assistant",
        "RAG combines retrieval with language model generation.",
    ),
    (
        "user",
        "Does it use embeddings?",
    ),
    (
        "assistant",
        "Embeddings are commonly used for vector retrieval.",
    ),
    (
        "user",
        "What about hybrid search?",
    ),
]

for role, content in messages:
    if role == "user":
        session.add_user_message(content)
    else:
        session.add_assistant_message(content)


print("\nSESSION ID")
print(session.session_id)

print("\nSUMMARY")
print(session.summary)

print("\nRECENT HISTORY")

for message in session.history:
    print(
        f"{message['role']}: "
        f"{message['content']}"
    )

print("\nHISTORY SENT TO RAG")

for message in session.get_history():
    print(
        f"{message['role']}: "
        f"{message['content']}"
    )