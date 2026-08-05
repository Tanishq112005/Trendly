from langchain_core.messages import SystemMessage, AIMessage
from pydantic import BaseModel, Field
from app.core.llm import llm
from app.modules.chat.state import AgentState
from app.modules.chat.tools import TicketTools


class PrepareTicket(BaseModel):
    """Call this to prepare a ticket before confirmation."""

    order_id: str = Field(description="The order ID")
    reason: str = Field(description="Brief reason for the ticket")
    summary: str = Field(description="Summary of the issue")


class TicketAgent:
    def __init__(self):
        self.llm = llm
        self.ticket_llm = self.llm.bind_tools([PrepareTicket])

    def invoke(self, state: AgentState) -> dict:
        """Handles human escalation."""
        user_name = state.get("name") or "the customer"
        user_email = state.get("email") or "Unknown"
        user_phone = state.get("phone") or "Unknown"

        sys_msg_text = f"""You are Trendly's escalation assistant. You are speaking to {user_name}. Greet them by their name if you know it.

Known Customer Details:
- Email: {user_email}
- Phone: {user_phone}

1. Gather the order ID and a brief reason.
2. Use the PrepareTicket tool to draft the ticket.
3. Be empathetic and professional."""

        sys_msg = SystemMessage(content=sys_msg_text)
        response = self.ticket_llm.invoke([sys_msg] + state["messages"])

        # Intercept PrepareTicket tool call for HITL
        if response.tool_calls:
            tool_call = response.tool_calls[0]
            if tool_call["name"] == "PrepareTicket":
                # Convert the tool call to a regular message so it doesn't trigger tools_condition
                hitl_msg = AIMessage(
                    content="I have prepared the ticket. Please confirm if you'd like me to create it."
                )
                return {
                    "messages": [hitl_msg],
                    "hitl_pending": True,
                    "ticket_details": tool_call["args"],
                }

        return {"messages": [response], "hitl_pending": False}


ticket_agent_instance = TicketAgent()
