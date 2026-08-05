from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.modules.chat.agent import graph


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


class ChatController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/chat", tags=["chat"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/", response_model=ChatResponse)
        async def chat_endpoint(req: ChatRequest):
            config = {"configurable": {"thread_id": req.session_id}, "recursion_limit": 15}
            
            # Handle HITL actions if present
            if req.hitl_action:
                state_dict = graph.get_state(config).values
                
                if req.hitl_action == "confirm" and req.ticket_details:
                    # Manually execute the tool since the agent was detached
                    from app.modules.chat.tools import TicketTools
                    res = TicketTools.escalate_to_human.invoke(req.ticket_details)
                    
                    # Update state with the result and clear hitl_pending
                    graph.update_state(
                        config, 
                        {"messages": [HumanMessage(content="I confirm. Please proceed."), AIMessage(content=res)], "hitl_pending": False}
                    )
                    return ChatResponse(response=res, session_id=req.session_id, hitl_pending=False)
                
                elif req.hitl_action == "cancel":
                    # Update state to reflect cancellation
                    graph.update_state(
                        config, 
                        {"messages": [HumanMessage(content="I have decided to cancel the ticket creation.")], "hitl_pending": False}
                    )
                    # Let the LLM respond to the cancellation
                    result = graph.invoke(None, config=config)
                else:
                    result = {"messages": state_dict.get("messages", [])}
            else:
                if not req.message or not req.message.strip():
                    raise HTTPException(status_code=400, detail="Message cannot be empty")
                
                result = graph.invoke(
                    {"messages": [HumanMessage(content=req.message)]}, 
                    config=config
                )
            
            # Read state values after invocation
            state_dict = graph.get_state(config).values
            hitl_pending = state_dict.get("hitl_pending", False)
            
            if hitl_pending:
                ticket_details = state_dict.get("ticket_details", {})
                return ChatResponse(
                    response="Are you sure you want to escalate this to a human? A support ticket will be created.", 
                    session_id=req.session_id,
                    hitl_pending=True,
                    ticket_details=ticket_details
                )
            
            # Normal completion
            messages = state_dict.get("messages", [])
            ai_response = messages[-1].content if messages else ""
            return ChatResponse(
                response=ai_response, 
                session_id=req.session_id,
                hitl_pending=False
            )


chat_controller = ChatController()
chat_router = chat_controller.router
