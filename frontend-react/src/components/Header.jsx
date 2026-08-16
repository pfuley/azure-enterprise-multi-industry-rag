function Header({
    account,
    isAuthenticated,
    isInteractionInProgress,
    onSignIn,
    onSignOut,
    onNewChat,
}) {
    return (
        <header className="header">

            <div>
                <h1>
                    Enterprise RAG Assistant
                </h1>

                <p>
                    Secure AI-powered enterprise knowledge
                </p>
            </div>


            <div className="header-actions">

                {isAuthenticated && account && (
                    <div className="user-info">

                        <span className="user-name">
                            {
                                account.name
                                || account.username
                                || "Signed-in user"
                            }
                        </span>

                        <span className="user-email">
                            {
                                account.username
                                || ""
                            }
                        </span>

                    </div>
                )}


                {isAuthenticated && (
                    <button
                        className="secondary-button"
                        onClick={onNewChat}
                        disabled={
                            isInteractionInProgress
                        }
                    >
                        New Chat
                    </button>
                )}


                {!isAuthenticated ? (

                    <button
                        className="primary-button"
                        onClick={onSignIn}
                        disabled={
                            isInteractionInProgress
                        }
                    >
                        {
                            isInteractionInProgress
                                ? "Signing in..."
                                : "Sign in"
                        }
                    </button>

                ) : (

                    <button
                        className="secondary-button"
                        onClick={onSignOut}
                        disabled={
                            isInteractionInProgress
                        }
                    >
                        {
                            isInteractionInProgress
                                ? "Please wait..."
                                : "Sign out"
                        }
                    </button>

                )}

            </div>

        </header>
    );
}


export default Header;