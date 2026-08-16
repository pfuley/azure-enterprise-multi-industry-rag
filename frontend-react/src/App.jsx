import {
    useEffect,
    useState,
} from "react";

import ChatInput from "./components/ChatInput";
import ChatWindow from "./components/ChatWindow";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";

import {
    deleteChatSession,
    getSessionHistory,
    getSessions,
    sendChatMessage,
} from "./services/api";

import {
    useAuth,
} from "./auth/useAuth";


function App() {

    const {
        account,
        isAuthenticated,
        isInteractionInProgress,
        signIn,
        signOut,
        getAccessToken,
    } = useAuth();


    const [
        sessionId,
        setSessionId,
    ] = useState(null);

    const [
        sessions,
        setSessions,
    ] = useState([]);

    const [
        messages,
        setMessages,
    ] = useState([]);

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        loadingSessions,
        setLoadingSessions,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");


    async function loadSessions() {

        if (!isAuthenticated) {
            return;
        }

        setLoadingSessions(
            true
        );

        try {

            const token =
                await getAccessToken();

            const result =
                await getSessions({
                    accessToken: token,
                });

            setSessions(
                result.sessions || []
            );

        } catch (requestError) {

            setError(
                requestError.message
            );

        } finally {

            setLoadingSessions(
                false
            );
        }
    }


    useEffect(
        () => {

            if (isAuthenticated) {

                loadSessions();

            } else {

                setSessions(
                    []
                );

                setMessages(
                    []
                );

                setSessionId(
                    null
                );
            }

        },
        [
            isAuthenticated,
        ]
    );


    async function handleSignIn() {

        if (
            isInteractionInProgress
        ) {
            return;
        }

        setError(
            ""
        );

        try {

            await signIn();

        } catch (signInError) {

            setError(
                signInError.message
            );
        }
    }


    async function handleSignOut() {

        if (
            isInteractionInProgress
        ) {
            return;
        }

        setError(
            ""
        );

        try {

            await signOut();

            setSessionId(
                null
            );

            setSessions(
                []
            );

            setMessages(
                []
            );

        } catch (signOutError) {

            setError(
                signOutError.message
            );
        }
    }


    async function handleSend(
        question
    ) {

        if (!isAuthenticated) {

            setError(
                "Please sign in before sending a message."
            );

            return;
        }


        setError(
            ""
        );


        const userMessage = {
            id:
                crypto.randomUUID(),

            role:
                "user",

            content:
                question,

            sources:
                [],
        };


        setMessages(
            previous => [
                ...previous,
                userMessage,
            ]
        );


        setLoading(
            true
        );


        try {

            const token =
                await getAccessToken();


            const result =
                await sendChatMessage({
                    question,
                    sessionId,
                    accessToken:
                        token,
                });


            setSessionId(
                result.session_id
            );


            const assistantMessage = {
                id:
                    crypto.randomUUID(),

                role:
                    "assistant",

                content:
                    result.answer,

                sources:
                    result.sources || [],
            };


            setMessages(
                previous => [
                    ...previous,
                    assistantMessage,
                ]
            );


            await loadSessions();

        } catch (requestError) {

            setError(
                requestError.message
            );

        } finally {

            setLoading(
                false
            );
        }
    }


    async function handleOpenSession(
        session
    ) {

        if (!isAuthenticated) {
            return;
        }


        setError(
            ""
        );

        setLoading(
            true
        );


        try {

            const token =
                await getAccessToken();


            const result =
                await getSessionHistory({
                    sessionId:
                        session.session_id,

                    accessToken:
                        token,
                });


            const restoredMessages = (
                result.messages || []
            ).map(
                message => ({
                    id:
                        crypto.randomUUID(),

                    role:
                        message.role,

                    content:
                        message.content,

                    sources:
                        [],
                })
            );


            setSessionId(
                session.session_id
            );


            setMessages(
                restoredMessages
            );

        } catch (requestError) {

            setError(
                requestError.message
            );

        } finally {

            setLoading(
                false
            );
        }
    }


    async function handleDeleteSession(
        sessionToDelete
    ) {

        if (!isAuthenticated) {
            return;
        }


        const confirmed =
            window.confirm(
                "Delete this conversation?"
            );


        if (!confirmed) {
            return;
        }


        setError(
            ""
        );


        try {

            const token =
                await getAccessToken();


            await deleteChatSession({
                sessionId:
                    sessionToDelete,

                accessToken:
                    token,
            });


            if (
                sessionId
                === sessionToDelete
            ) {

                setSessionId(
                    null
                );

                setMessages(
                    []
                );
            }


            await loadSessions();

        } catch (requestError) {

            setError(
                requestError.message
            );
        }
    }


    function handleNewChat() {

        setSessionId(
            null
        );

        setMessages(
            []
        );

        setError(
            ""
        );
    }


    return (
        <div className="application">

            {isAuthenticated && (
                <Sidebar
                    sessions={
                        sessions
                    }

                    activeSessionId={
                        sessionId
                    }

                    onOpenSession={
                        handleOpenSession
                    }

                    onDeleteSession={
                        handleDeleteSession
                    }

                    onNewChat={
                        handleNewChat
                    }

                    loadingSessions={
                        loadingSessions
                    }
                />
            )}


            <div className="app-shell">

                <Header
                    account={
                        account
                    }

                    isAuthenticated={
                        isAuthenticated
                    }

                    isInteractionInProgress={
                        isInteractionInProgress
                    }

                    onSignIn={
                        handleSignIn
                    }

                    onSignOut={
                        handleSignOut
                    }

                    onNewChat={
                        handleNewChat
                    }
                />


                {!isAuthenticated ? (

                    <main className="chat-container">

                        <div className="welcome-message">

                            <h2>
                                Enterprise knowledge,
                                securely retrieved
                            </h2>

                            <p>
                                Sign in with Microsoft
                                to access your authorised
                                knowledge base.
                            </p>

                            <button
                                className="sign-in-button"
                                onClick={
                                    handleSignIn
                                }
                                disabled={
                                    isInteractionInProgress
                                }
                            >
                                {
                                    isInteractionInProgress
                                        ? "Signing in..."
                                        : "Sign in with Microsoft"
                                }
                            </button>

                        </div>

                    </main>

                ) : (

                    <ChatWindow
                        messages={
                            messages
                        }

                        loading={
                            loading
                        }
                    />

                )}


                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}


                {isAuthenticated && (
                    <ChatInput
                        onSend={
                            handleSend
                        }

                        loading={
                            loading
                        }
                    />
                )}

            </div>

        </div>
    );
}


export default App;