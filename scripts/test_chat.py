from src.rag.chat_service import RAGChatService
from src.security.authorization import AuthorizationContext


def print_result(title: str, result: dict) -> None:
    print(f"\n{title}")
    print("=" * 60)

    print("\nSEARCH QUERY")
    print(result["search_query"])

    print("\nANSWER")
    print(result["answer"])

    print("\nSESSION ID")
    print(result["session_id"])

    print("\nSOURCES")

    if not result["sources"]:
        print("No sources returned.")

    for source in result["sources"]:
        print(
            f"File: {source['file_name']} | "
            f"Page: {source['page_number']} | "
            f"Chunk: {source['chunk_id']}"
        )

    print("\nRETRIEVAL TRACE")

    if not result["retrieval_trace"]:
        print("No authorised chunks retrieved.")

    for item in result["retrieval_trace"]:
        print(
            f"Chunk: {item['chunk_id']} | "
            f"File: {item['file_name']} | "
            f"Page: {item['page_number']} | "
            f"Search Score: {item['search_score']} | "
            f"Reranker Score: {item['reranker_score']}"
        )


# =========================================================
# TEST 1: AUTHORISED USER
# =========================================================

authorized_user = AuthorizationContext(
    user_id="user-001",
    roles=[
        "employee",
    ],
    groups=[
        "service-desk",
        "it-admins",
    ],
    allowed_industries=[
        "it-support",
    ],
    allowed_departments=[
        "service-desk",
    ],
    max_classification="internal",
)


authorized_chat = RAGChatService(
    auth=authorized_user
)


question_1 = "What is retrieval augmented generation?"

result_1 = authorized_chat.ask(
    question_1
)

print_result(
    "TEST 1 - AUTHORISED USER",
    result_1,
)


# =========================================================
# TEST 2: MULTI-TURN QUESTION
# =========================================================

question_2 = "Why is it useful?"

result_2 = authorized_chat.ask(
    question_2
)

print_result(
    "TEST 2 - AUTHORISED MULTI-TURN QUESTION",
    result_2,
)


print("\nAUTHORIZED USER SESSION HISTORY")
print("=" * 60)

for message in authorized_chat.get_history():
    print(
        f"{message['role']}: "
        f"{message['content']}"
    )


print("\nAUTHORIZED USER CONTEXT")
print("=" * 60)

auth_context = (
    authorized_chat.get_authorization_context()
)

print("User ID:", auth_context.user_id)
print("Roles:", auth_context.roles)
print("Groups:", auth_context.groups)

print(
    "Allowed Industries:",
    auth_context.allowed_industries,
)

print(
    "Allowed Departments:",
    auth_context.allowed_departments,
)

print(
    "Maximum Classification:",
    auth_context.max_classification,
)


# =========================================================
# TEST 3: UNAUTHORISED USER
# =========================================================

unauthorized_user = AuthorizationContext(
    user_id="user-002",
    roles=[
        "employee",
    ],
    groups=[
        "finance-team",
    ],
    allowed_industries=[
        "it-support",
    ],
    allowed_departments=[
        "service-desk",
    ],
    max_classification="internal",
)


unauthorized_chat = RAGChatService(
    auth=unauthorized_user
)


question_3 = "What is retrieval augmented generation?"

result_3 = unauthorized_chat.ask(
    question_3
)

print_result(
    "TEST 3 - UNAUTHORISED USER",
    result_3,
)


print("\nUNAUTHORISED USER CONTEXT")
print("=" * 60)

unauthorized_context = (
    unauthorized_chat.get_authorization_context()
)

print(
    "User ID:",
    unauthorized_context.user_id,
)

print(
    "Roles:",
    unauthorized_context.roles,
)

print(
    "Groups:",
    unauthorized_context.groups,
)

print(
    "Allowed Industries:",
    unauthorized_context.allowed_industries,
)

print(
    "Allowed Departments:",
    unauthorized_context.allowed_departments,
)

print(
    "Maximum Classification:",
    unauthorized_context.max_classification,
)