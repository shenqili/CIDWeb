from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_env: str
    database: bool


class MessageResponse(BaseModel):
    message: str


class ListResponse(BaseModel):
    items: list[Any]
