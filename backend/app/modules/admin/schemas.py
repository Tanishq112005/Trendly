from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class TicketModel(BaseModel):
    id: str
    session_id: str
    summary: str
    status: str
    resolution: Optional[str] = None


class ResolveRequest(BaseModel):
    resolution: str
