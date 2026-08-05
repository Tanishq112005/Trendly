from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    message: str | None = None
    hitl_action: str | None = None  # "confirm" or "cancel"
    ticket_details: dict | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    hitl_pending: bool = False
    ticket_details: dict | None = None


class PrepareTicket(BaseModel):
    """Call this to prepare a ticket before confirmation."""

    order_id: str = Field(description="The order ID")
    reason: str = Field(description="Brief reason for the ticket")
    summary: str = Field(description="Summary of the issue")


class RouterDecision(BaseModel):
    intent: str = Field(
        description="The user's intent. Must be exactly 'product_agent', 'ticket_agent', 'policy_agent', or 'unrelated_agent'."
    )
