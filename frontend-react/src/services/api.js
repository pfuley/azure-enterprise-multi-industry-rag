const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL;


async function parseResponse(
    response
) {
    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data.message
            || data.detail
            || "The request failed."
        );
    }

    return data;
}


export async function sendChatMessage({
    question,
    sessionId,
    accessToken,
}) {
    const body = {
        question,
    };

    if (sessionId) {
        body.session_id = sessionId;
    }

    const response = await fetch(
        `${API_BASE_URL}/chat`,
        {
            method: "POST",

            headers: {
                Authorization:
                    `Bearer ${accessToken}`,

                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify(
                body
            ),
        }
    );

    return parseResponse(
        response
    );
}


export async function getSessions({
    accessToken,
}) {
    const response = await fetch(
        `${API_BASE_URL}/sessions`,
        {
            method: "GET",

            headers: {
                Authorization:
                    `Bearer ${accessToken}`,
            },
        }
    );

    return parseResponse(
        response
    );
}


export async function getSessionHistory({
    sessionId,
    accessToken,
}) {
    const response = await fetch(
        `${API_BASE_URL}/sessions/${sessionId}/history`,
        {
            method: "GET",

            headers: {
                Authorization:
                    `Bearer ${accessToken}`,
            },
        }
    );

    return parseResponse(
        response
    );
}


export async function deleteChatSession({
    sessionId,
    accessToken,
}) {
    const response = await fetch(
        `${API_BASE_URL}/sessions/${sessionId}`,
        {
            method: "DELETE",

            headers: {
                Authorization:
                    `Bearer ${accessToken}`,
            },
        }
    );

    return parseResponse(
        response
    );
}