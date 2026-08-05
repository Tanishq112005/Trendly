from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import db_manager

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

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

@admin_router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    # Hardcoded auth for now
    if req.username == "admin" and req.password == "password":
        return LoginResponse(token="fake-jwt-token-12345")
    raise HTTPException(status_code=401, detail="Invalid credentials")

@admin_router.get("/tickets", response_model=List[TicketModel])
async def get_tickets():
    tickets = await db_manager.get_all_tickets()
    # Pydantic validates and returns the list of dicts
    return tickets

@admin_router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, req: ResolveRequest):
    try:
        await db_manager.resolve_ticket(ticket_id, req.resolution)
        return {"status": "success", "message": f"Ticket {ticket_id} resolved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
