function Sidebar({
    sessions,
    activeSessionId,
    onOpenSession,
    onDeleteSession,
    onNewChat,
    loadingSessions,
}) {
    return (
        <aside className="sidebar">

            <div className="sidebar-header">
                <div>
                    <h2>
                        Conversations
                    </h2>

                    <p>
                        Saved in Cosmos DB
                    </p>
                </div>

                <button
                    className="new-chat-button"
                    onClick={onNewChat}
                >
                    +
                </button>
            </div>


            <div className="sidebar-content">

                {loadingSessions && (
                    <div className="sidebar-status">
                        Loading conversations...
                    </div>
                )}


                {!loadingSessions
                    && sessions.length === 0
                    && (
                        <div className="sidebar-status">
                            No conversations yet.
                        </div>
                    )
                }


                {sessions.map(
                    session => {

                        const isActive =
                            session.session_id
                            === activeSessionId;

                        return (
                            <div
                                key={
                                    session.session_id
                                }
                                className={
                                    isActive
                                        ? "session-item session-item-active"
                                        : "session-item"
                                }
                            >

                                <button
                                    className="session-open-button"
                                    onClick={
                                        () =>
                                            onOpenSession(
                                                session
                                            )
                                    }
                                >
                                    <span className="session-title">
                                        {
                                            session.title
                                            || "Untitled conversation"
                                        }
                                    </span>

                                    <span className="session-date">
                                        {
                                            new Date(
                                                session.last_accessed_at
                                            )
                                                .toLocaleString()
                                        }
                                    </span>
                                </button>


                                <button
                                    className="session-delete-button"
                                    title="Delete conversation"
                                    onClick={
                                        event => {
                                            event.stopPropagation();

                                            onDeleteSession(
                                                session.session_id
                                            );
                                        }
                                    }
                                >
                                    ×
                                </button>

                            </div>
                        );
                    }
                )}

            </div>

        </aside>
    );
}


export default Sidebar;