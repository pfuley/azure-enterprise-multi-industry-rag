from src.session.cosmos_store import (
    CosmosSessionStore,
)


store = CosmosSessionStore()


session = store.create_session(
    user_id="cosmos-test-user"
)

print(
    "Session created:",
    session.session_id,
)


store.add_message(
    session_id=session.session_id,
    role="user",
    content="What is RAG?",
)

store.add_message(
    session_id=session.session_id,
    role="assistant",
    content="Test response",
)


messages = store.get_messages(
    session_id=session.session_id,
    user_id="cosmos-test-user",
)


print("\nMESSAGES")
print("=" * 60)

for message in messages:
    print(
        message.sequence,
        message.role,
        message.content,
    )


deleted = store.delete_session(
    session_id=session.session_id,
    user_id="cosmos-test-user",
)

print(
    "\nDeleted:",
    deleted,
)