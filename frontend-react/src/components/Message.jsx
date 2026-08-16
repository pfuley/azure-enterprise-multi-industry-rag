import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import SourceList from "./SourceList";


function Message({
    message,
}) {
    const isUser =
        message.role === "user";

    return (
        <div
            className={
                isUser
                    ? "message message-user"
                    : "message message-assistant"
            }
        >

            <div className="message-role">
                {
                    isUser
                        ? "You"
                        : "Assistant"
                }
            </div>


            <div className="message-content">

                {isUser ? (

                    message.content

                ) : (

                    <ReactMarkdown
                        remarkPlugins={[
                            remarkGfm,
                        ]}
                    >
                        {message.content}
                    </ReactMarkdown>

                )}

            </div>


            {!isUser && (
                <SourceList
                    sources={
                        message.sources
                    }
                />
            )}

        </div>
    );
}


export default Message;