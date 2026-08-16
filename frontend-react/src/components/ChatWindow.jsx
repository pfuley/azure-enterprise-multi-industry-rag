import {
    useEffect,
    useRef,
} from "react";

import Message from "./Message";


function ChatWindow({
    messages,
    loading,
}) {
    const bottomRef =
        useRef(null);

    useEffect(
        () => {
            bottomRef.current?.scrollIntoView({
                behavior: "smooth",
            });
        },
        [
            messages,
            loading,
        ]
    );

    if (!messages.length) {
        return (
            <main className="chat-container">
                <div className="welcome-message">
                    <h2>
                        How can I help?
                    </h2>

                    <p>
                        Ask a question about your
                        authorised enterprise knowledge base.
                    </p>
                </div>
            </main>
        );
    }

    return (
        <main className="chat-container">
            {messages.map(
                message => (
                    <Message
                        key={message.id}
                        message={message}
                    />
                )
            )}

            {loading && (
                <div className="message message-assistant loading">
                    <div className="message-role">
                        Assistant
                    </div>

                    Searching the knowledge base...
                </div>
            )}

            <div ref={bottomRef} />
        </main>
    );
}


export default ChatWindow;