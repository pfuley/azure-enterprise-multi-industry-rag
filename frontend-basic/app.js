const API_BASE_URL =
    "http://127.0.0.1:8000/api/v1";


let sessionId = null;

let accessToken = null;


const chatContainer =
    document.getElementById(
        "chat-container"
    );


const chatForm =
    document.getElementById(
        "chat-form"
    );


const questionInput =
    document.getElementById(
        "question-input"
    );


const sendButton =
    document.getElementById(
        "send-button"
    );


const newChatButton =
    document.getElementById(
        "new-chat-button"
    );


const errorMessage =
    document.getElementById(
        "error-message"
    );


function requestAccessToken() {

    const token = window.prompt(
        "Paste your temporary Microsoft Entra access token:"
    );

    if (!token) {

        showError(
            "An access token is required."
        );

        return false;
    }

    accessToken = token.trim();

    return true;
}


function addMessage(
    role,
    content,
    sources = []
) {

    const welcome =
        document.querySelector(
            ".welcome-message"
        );

    if (welcome) {
        welcome.remove();
    }


    const message =
        document.createElement(
            "div"
        );


    message.classList.add(
        "message"
    );


    if (role === "user") {

        message.classList.add(
            "message-user"
        );

    } else {

        message.classList.add(
            "message-assistant"
        );
    }


    const roleElement =
        document.createElement(
            "span"
        );


    roleElement.classList.add(
        "message-role"
    );


    roleElement.textContent =
        role === "user"
            ? "You"
            : "Assistant";


    const contentElement =
        document.createElement(
            "div"
        );


    contentElement.textContent =
        content;


    message.appendChild(
        roleElement
    );


    message.appendChild(
        contentElement
    );


    if (
        role === "assistant"
        && sources.length > 0
    ) {

        const sourcesElement =
            document.createElement(
                "div"
            );


        sourcesElement.classList.add(
            "sources"
        );


        const title =
            document.createElement(
                "div"
            );


        title.classList.add(
            "sources-title"
        );


        title.textContent =
            "Sources";


        sourcesElement.appendChild(
            title
        );


        const uniqueSources = [
            ...new Map(
                sources.map(
                    source => [
                        source.file_name,
                        source
                    ]
                )
            ).values()
        ];


        uniqueSources.forEach(
            source => {

                const sourceElement =
                    document.createElement(
                        "div"
                    );


                sourceElement.classList.add(
                    "source"
                );


                sourceElement.textContent =
                    source.page_number
                        ? `${source.file_name} — Page ${source.page_number}`
                        : source.file_name;


                sourcesElement.appendChild(
                    sourceElement
                );
            }
        );


        message.appendChild(
            sourcesElement
        );
    }


    chatContainer.appendChild(
        message
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


function showError(
    message
) {

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );
}


function hideError() {

    errorMessage.classList.add(
        "hidden"
    );
}


function setLoading(
    loading
) {

    sendButton.disabled =
        loading;

    questionInput.disabled =
        loading;

    sendButton.textContent =
        loading
            ? "Sending..."
            : "Send";
}


async function sendQuestion(
    question
) {

    if (!accessToken) {

        const tokenAvailable =
            requestAccessToken();

        if (!tokenAvailable) {
            return;
        }
    }


    hideError();

    setLoading(
        true
    );


    addMessage(
        "user",
        question
    );


    const requestBody = {
        question: question
    };


    if (sessionId) {

        requestBody.session_id =
            sessionId;
    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${accessToken}`,

                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            requestBody
                        )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            if (response.status === 401) {

                accessToken = null;

                throw new Error(
                    "Authentication failed or the token expired. Try again with a fresh token."
                );
            }


            throw new Error(
                data.message
                || data.detail
                || "The request failed."
            );
        }


        sessionId =
            data.session_id;


        addMessage(
            "assistant",
            data.answer,
            data.sources || []
        );

    } catch (error) {

        showError(
            error.message
        );

    } finally {

        setLoading(
            false
        );

        questionInput.focus();
    }
}


chatForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();

        const question =
            questionInput
                .value
                .trim();


        if (!question) {
            return;
        }


        questionInput.value =
            "";


        await sendQuestion(
            question
        );
    }
);


newChatButton.addEventListener(
    "click",
    () => {

        sessionId = null;

        chatContainer.innerHTML = `
            <div class="welcome-message">
                <h2>New conversation</h2>

                <p>
                    Ask a question about the
                    authorised enterprise
                    knowledge base.
                </p>
            </div>
        `;

        hideError();

        questionInput.focus();
    }
);


requestAccessToken();