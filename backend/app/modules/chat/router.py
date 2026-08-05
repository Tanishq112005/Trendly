from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.modules.chat.agent import graph


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


class ChatController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/chat", tags=["chat"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/", response_model=ChatResponse)
        async def chat_endpoint(req: ChatRequest):
            if not req.message.strip():
                raise HTTPException(status_code=400, detail="Message cannot be empty")

            config = {"configurable": {"thread_id": req.session_id}}
            result = graph.invoke(
                {"messages": [HumanMessage(content=req.message)]}, config=config
            )
            ai_response = result["messages"][-1].content
            return ChatResponse(response=ai_response, session_id=req.session_id)


chat_controller = ChatController()
chat_router = chat_controller.router
