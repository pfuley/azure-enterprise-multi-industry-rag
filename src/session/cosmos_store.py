from datetime import datetime, timezone
from uuid import uuid4

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
)
from azure.identity import (
    DefaultAzureCredential,
)

from src.api.exceptions import (
    APIServiceError,
)
from src.core.config import (
    AZURE_COSMOS_DATABASE_NAME,
    AZURE_COSMOS_ENDPOINT,
    AZURE_COSMOS_SESSION_CONTAINER_NAME,
)
from src.session.base import (
    SessionStore,
)
from src.session.models import (
    PersistedMessage,
    PersistedSession,
)


class CosmosSessionStore(
    SessionStore
):
    """
    Persistent conversation store backed by
    Azure Cosmos DB for NoSQL.

    Partition key:
        /session_id

    Each conversation partition contains:
    - one session metadata item
    - zero or more message items
    """

    def __init__(
        self,
    ):
        # -------------------------------------
        # 1. Validate configuration
        # -------------------------------------

        if not AZURE_COSMOS_ENDPOINT:
            raise ValueError(
                "AZURE_COSMOS_ENDPOINT "
                "is not configured"
            )

        if not AZURE_COSMOS_DATABASE_NAME:
            raise ValueError(
                "AZURE_COSMOS_DATABASE_NAME "
                "is not configured"
            )

        if not (
            AZURE_COSMOS_SESSION_CONTAINER_NAME
        ):
            raise ValueError(
                "AZURE_COSMOS_SESSION_CONTAINER_NAME "
                "is not configured"
            )

        # -------------------------------------
        # 2. Azure authentication
        #
        # Local:
        # az login / developer identity
        #
        # Production:
        # Managed Identity
        # -------------------------------------

        credential = (
            DefaultAzureCredential()
        )

        # -------------------------------------
        # 3. Create Cosmos client
        # -------------------------------------

        client = CosmosClient(
            url=AZURE_COSMOS_ENDPOINT,
            credential=credential,
        )

        database = (
            client.get_database_client(
                AZURE_COSMOS_DATABASE_NAME
            )
        )

        self.container = (
            database.get_container_client(
                AZURE_COSMOS_SESSION_CONTAINER_NAME
            )
        )

    def _service_error(
        self,
        error: Exception,
    ) -> APIServiceError:
        """
        Convert Cosmos failures into a safe
        application-level service error.
        """

        return APIServiceError(
            error_code=(
                "session_store_unavailable"
            ),
            message=(
                "The conversation storage service "
                "is temporarily unavailable."
            ),
        )

    def create_session(
        self,
        user_id: str,
        title: str | None = None,
    ) -> PersistedSession:
        """
        Create persistent conversation metadata.
        """

        session_id = str(
            uuid4()
        )

        now = datetime.now(
            timezone.utc
        )

        item = {
            "id":
                session_id,

            "session_id":
                session_id,

            "type":
                "session",

            "user_id":
                user_id,

            "title":
                title,

            "created_at":
                now.isoformat(),

            "last_accessed_at":
                now.isoformat(),
        }

        try:
            self.container.create_item(
                body=item
            )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        return PersistedSession(
            id=session_id,
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_accessed_at=now,
            title=title,
        )

    def get_session(
        self,
        session_id: str,
        user_id: str,
    ) -> PersistedSession | None:
        """
        Retrieve session metadata and enforce
        ownership.
        """

        try:
            item = (
                self.container.read_item(
                    item=session_id,
                    partition_key=session_id,
                )
            )

        except CosmosResourceNotFoundError:
            return None

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        if item.get(
            "type"
        ) != "session":
            return None

        # -------------------------------------
        # Security:
        # session IDs do not grant access.
        # The authenticated user must own it.
        # -------------------------------------

        if item.get(
            "user_id"
        ) != user_id:
            raise PermissionError(
                "The session does not belong "
                "to the authenticated user."
            )

        now = datetime.now(
            timezone.utc
        )

        item[
            "last_accessed_at"
        ] = now.isoformat()

        try:
            self.container.replace_item(
                item=item["id"],
                body=item,
            )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        return PersistedSession(
            id=item[
                "id"
            ],

            session_id=item[
                "session_id"
            ],

            user_id=item[
                "user_id"
            ],

            created_at=(
                datetime.fromisoformat(
                    item[
                        "created_at"
                    ]
                )
            ),

            last_accessed_at=now,

            title=item.get(
                "title"
            ),
        )

    def list_sessions(
        self,
        user_id: str,
    ) -> list[PersistedSession]:
        """
        Return all sessions owned by one user.

        Because the container is partitioned by
        /session_id, listing sessions for one user
        requires a cross-partition query.
        """

        try:
            items = list(
                self.container.query_items(
                    query=(
                        "SELECT * FROM c "
                        "WHERE c.type = 'session' "
                        "AND c.user_id = @user_id "
                        "ORDER BY "
                        "c.last_accessed_at DESC"
                    ),
                    parameters=[
                        {
                            "name":
                                "@user_id",

                            "value":
                                user_id,
                        }
                    ],
                    enable_cross_partition_query=True,
                )
            )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        return [
            PersistedSession(
                id=item[
                    "id"
                ],

                session_id=item[
                    "session_id"
                ],

                user_id=item[
                    "user_id"
                ],

                created_at=(
                    datetime.fromisoformat(
                        item[
                            "created_at"
                        ]
                    )
                ),

                last_accessed_at=(
                    datetime.fromisoformat(
                        item[
                            "last_accessed_at"
                        ]
                    )
                ),

                title=item.get(
                    "title"
                ),
            )
            for item in items
        ]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> PersistedMessage:
        """
        Add one user or assistant message to
        an existing conversation partition.
        """

        if role not in {
            "user",
            "assistant",
        }:
            raise ValueError(
                "Message role must be "
                "'user' or 'assistant'."
            )

        # -------------------------------------
        # 1. Determine next sequence number
        # -------------------------------------

        try:
            counts = list(
                self.container.query_items(
                    query=(
                        "SELECT VALUE COUNT(1) "
                        "FROM c "
                        "WHERE "
                        "c.session_id = @session_id "
                        "AND c.type = 'message'"
                    ),
                    parameters=[
                        {
                            "name":
                                "@session_id",

                            "value":
                                session_id,
                        }
                    ],
                    partition_key=(
                        session_id
                    ),
                )
            )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        sequence = (
            counts[0]
            if counts
            else 0
        ) + 1

        # -------------------------------------
        # 2. Create message
        # -------------------------------------

        message_id = str(
            uuid4()
        )

        now = datetime.now(
            timezone.utc
        )

        item = {
            "id":
                message_id,

            "session_id":
                session_id,

            "type":
                "message",

            "role":
                role,

            "content":
                content,

            "sequence":
                sequence,

            "created_at":
                now.isoformat(),
        }

        try:
            self.container.create_item(
                body=item
            )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        return PersistedMessage(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            sequence=sequence,
            created_at=now,
        )

    def get_messages(
        self,
        session_id: str,
        user_id: str,
    ) -> list[PersistedMessage]:
        """
        Return persisted conversation messages
        in sequence order.
        """

        # -------------------------------------
        # 1. Validate session ownership first
        # -------------------------------------

        session = self.get_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            return []

        # -------------------------------------
        # 2. Read conversation messages
        # -------------------------------------

        try:
            items = list(
                self.container.query_items(
                    query=(
                        "SELECT * "
                        "FROM c "
                        "WHERE "
                        "c.session_id = @session_id "
                        "AND c.type = 'message' "
                        "ORDER BY c.sequence ASC"
                    ),
                    parameters=[
                        {
                            "name":
                                "@session_id",

                            "value":
                                session_id,
                        }
                    ],
                    partition_key=(
                        session_id
                    ),
                )
            )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        return [
            PersistedMessage(
                id=item[
                    "id"
                ],

                session_id=item[
                    "session_id"
                ],

                role=item[
                    "role"
                ],

                content=item[
                    "content"
                ],

                sequence=item[
                    "sequence"
                ],

                created_at=(
                    datetime.fromisoformat(
                        item[
                            "created_at"
                        ]
                    )
                ),
            )
            for item in items
        ]

    def delete_session(
        self,
        session_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete session metadata and every message
        belonging to the conversation partition.
        """

        # -------------------------------------
        # 1. Validate ownership
        # -------------------------------------

        session = self.get_session(
            session_id=session_id,
            user_id=user_id,
        )

        if session is None:
            return False

        # -------------------------------------
        # 2. Find every item in this partition
        # -------------------------------------

        try:
            items = list(
                self.container.query_items(
                    query=(
                        "SELECT c.id "
                        "FROM c "
                        "WHERE "
                        "c.session_id = @session_id"
                    ),
                    parameters=[
                        {
                            "name":
                                "@session_id",

                            "value":
                                session_id,
                        }
                    ],
                    partition_key=(
                        session_id
                    ),
                )
            )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        # -------------------------------------
        # 3. Delete all items in the partition
        # -------------------------------------

        try:
            for item in items:

                self.container.delete_item(
                    item=item[
                        "id"
                    ],
                    partition_key=(
                        session_id
                    ),
                )

        except CosmosHttpResponseError as error:
            raise self._service_error(
                error
            ) from error

        return True