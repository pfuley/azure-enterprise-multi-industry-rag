from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.exceptions import APIServiceError
from src.api.routes import router


app = FastAPI(
    title="Enterprise Multi-Industry RAG API",
    description=(
        "Secure enterprise Retrieval-Augmented "
        "Generation API."
    ),
    version="1.0.0",
)


ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


@app.exception_handler(
    APIServiceError
)
async def api_service_error_handler(
    request: Request,
    exc: APIServiceError,
):
    return JSONResponse(
        status_code=503,
        content={
            "error":
                exc.error_code,
            "message":
                exc.message,
        },
    )


@app.exception_handler(
    Exception
)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
):
    # Later in Commit 14 this will be
    # logged/traced with OpenTelemetry.
    print(
        "UNEXPECTED API ERROR:",
        type(exc).__name__,
        str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error":
                "internal_server_error",
            "message": (
                "An unexpected server error occurred."
            ),
        },
    )


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy"
    }


app.include_router(
    router,
    prefix="/api/v1",
)