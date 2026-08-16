from pydantic import BaseModel


class APIErrorResponse(BaseModel):
    error: str
    message: str