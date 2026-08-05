from fastapi import APIRouter, HTTPException
from typing import List
from app.modules.admin.schemas import LoginRequest, LoginResponse, TicketModel, ResolveRequest
from app.modules.admin.service import AdminService

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@admin_router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    if AdminService.verify_credentials(req.username, req.password):
        return LoginResponse(token="fake-jwt-token-12345")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@admin_router.get("/tickets", response_model=List[TicketModel])
async def get_tickets():
    tickets = await AdminService.get_all_tickets()
    return tickets


@admin_router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(ticket_id: str, req: ResolveRequest):
    try:
        await AdminService.resolve_ticket(ticket_id, req.resolution)
        return {"status": "success", "message": f"Ticket {ticket_id} resolved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
