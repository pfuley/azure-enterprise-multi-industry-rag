import {
    useState,
} from "react";


function ChatInput({
    onSend,
    loading,
}) {
    const [
        question,
        setQuestion,
    ] = useState("");


    async function handleSubmit(
        event
    ) {
        event.preventDefault();

        const trimmedQuestion =
            question.trim();

        if (
            !trimmedQuestion
            || loading
        ) {
            return;
        }

        setQuestion("");

        await onSend(
            trimmedQuestion
        );
    }


    return (
        <form
            className="chat-form"
            onSubmit={handleSubmit}
        >
            <textarea
                value={question}

                onChange={
                    event =>
                        setQuestion(
                            event.target.value
                        )
                }

                placeholder="Ask a question..."

                rows="1"

                maxLength="4000"

                disabled={loading}
            />

            <button
                type="submit"
                disabled={loading}
            >
                {loading
                    ? "Sending..."
                    : "Send"}
            </button>
        </form>
    );
}


export default ChatInput;