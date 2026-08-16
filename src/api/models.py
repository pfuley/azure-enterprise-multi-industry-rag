from typing import Any

from pydantic import (
    BaseModel,
    Field,
)


# =========================================================
# CHAT REQUEST
# =========================================================

class ChatRequest(BaseModel):
    """
    Request sent by a frontend client to the
    enterprise RAG chat endpoint.

    session_id:
        None = start a new conversation.

        Existing ID = continue a persisted
        Cosmos DB conversation.
    """

    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    session_id: str | None = None


# =========================================================
# CHAT RESPONSE
# =========================================================

class ChatResponse(BaseModel):
    """
    Response returned after the secure RAG
    pipeline processes a question.
    """

    answer: str

    session_id: str

    search_query: str

    guardrail_blocked: bool

    guardrail_reason: str | None = None

    sources: list[dict[str, Any]] = Field(
        default_factory=list
    )


# =========================================================
# SESSION SUMMARY
# =========================================================

class SessionSummaryResponse(BaseModel):
    """
    Lightweight representation of one conversation.

    Used by the React sidebar so we do not need to
    load every message for every conversation.
    """

    session_id: str

    title: str | None = None

    created_at: str

    last_accessed_at: str


# =========================================================
# SESSION LIST
# =========================================================

class SessionListResponse(BaseModel):
    """
    Response returned by:

        GET /api/v1/sessions
    """

    sessions: list[
        SessionSummaryResponse
    ] = Field(
        default_factory=list
    )


# =========================================================
# SESSION MESSAGE
# =========================================================

class SessionMessageResponse(BaseModel):
    """
    One persisted conversation message returned
    to a frontend when reopening a conversation.
    """

    role: str

    content: str


# =========================================================
# SESSION HISTORY
# =========================================================

class SessionHistoryResponse(BaseModel):
    """
    Response returned by:

        GET /api/v1/sessions/{session_id}/history
    """

    session_id: str

    messages: list[
        SessionMessageResponse
    ] = Field(
        default_factory=list
    )


# =========================================================
# SESSION DELETE
# =========================================================

class SessionDeleteResponse(BaseModel):
    """
    Response returned by:

        DELETE /api/v1/sessions/{session_id}
    """

    session_id: str

    deleted: bool