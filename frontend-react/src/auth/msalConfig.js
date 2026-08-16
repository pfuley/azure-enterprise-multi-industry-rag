export const msalConfig = {
    auth: {
        clientId:
            import.meta.env.VITE_ENTRA_CLIENT_ID,

        authority:
            `https://login.microsoftonline.com/${import.meta.env.VITE_ENTRA_TENANT_ID}`,

        redirectUri:
            "http://localhost:5173/redirect.html",

        postLogoutRedirectUri:
            "http://localhost:5173/",
    },

    cache: {
        cacheLocation:
            "sessionStorage",
    },
};


export const loginRequest = {
    scopes: [
        `api://${import.meta.env.VITE_RAG_API_CLIENT_ID}/RAG.Access`,
    ],
};