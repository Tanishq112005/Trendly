from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from app.modules.chat.agent import graph
from app.core.database import db_manager


from app.modules.chat.schemas import ChatRequest, ChatResponse


class ChatController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/chat", tags=["chat"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/", response_model=ChatResponse)
        async def chat_endpoint(req: ChatRequest):
            config = {
                "configurable": {"thread_id": req.session_id},
                "recursion_limit": 15,
            }

            # Handle HITL actions if present
            if req.hitl_action:
                state_dict = graph.get_state(config).values

                if req.hitl_action == "confirm" and req.ticket_details:
                    from app.core.redis_client import redis_manager

                    # Create ticket in MongoDB and embed full chat history state
                    from langchain_core.messages import messages_to_dict

                    current_state_dict = state_dict.copy()
                    if "messages" in current_state_dict:
                        current_state_dict["messages"] = messages_to_dict(
                            current_state_dict["messages"]
                        )

                    ticket_id = await db_manager.create_ticket(
                        req.session_id, current_state_dict
                    )

                    # Trigger the Redis Pub/Sub event for the worker
                    await redis_manager.publish_ticket(req.session_id, ticket_id)

                    # Update state with the result and clear hitl_pending
                    graph.update_state(
                        config,
                        {
                            "messages": [
                                HumanMessage(content="I confirm. Please proceed."),
                                AIMessage(
                                    content=f"Your support ticket (#{ticket_id}) has been created successfully. A human agent will review it shortly."
                                ),
                            ],
                            "hitl_pending": False,
                        },
                    )

                    return ChatResponse(
                        response=f"Your support ticket (#{ticket_id}) has been created successfully. A human agent will review it shortly.",
                        session_id=req.session_id,
                        hitl_pending=False,
                    )

                elif req.hitl_action == "cancel":
                    # Update state to reflect cancellation
                    graph.update_state(
                        config,
                        {
                            "messages": [
                                HumanMessage(
                                    content="I have decided to cancel the ticket creation."
                                )
                            ],
                            "hitl_pending": False,
                        },
                    )
                    # Let the LLM respond to the cancellation
                    result = graph.invoke(None, config=config)
                else:
                    result = {"messages": state_dict.get("messages", [])}
            else:
                if not req.message or not req.message.strip():
                    raise HTTPException(
                        status_code=400, detail="Message cannot be empty"
                    )

                from app.core.semantic_cache import semantic_cache
                
                if semantic_cache:
                    cached_response = await semantic_cache.check_cache(req.message)
                    if cached_response:
                        graph.update_state(
                            config,
                            {"messages": [HumanMessage(content=req.message), AIMessage(content=cached_response)]}
                        )
                        return ChatResponse(
                            response=cached_response, session_id=req.session_id, hitl_pending=False
                        )

                result = graph.invoke(
                    {"messages": [HumanMessage(content=req.message)]}, config=config
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
                    ticket_details=ticket_details,
                )

            # Normal completion
            messages = state_dict.get("messages", [])
            ai_response = messages[-1].content if messages else ""
            next_node = state_dict.get("next_node")

            if next_node == "policy_agent" and not req.hitl_action:
                from app.core.semantic_cache import semantic_cache
                if semantic_cache:
                    import asyncio
                    asyncio.create_task(semantic_cache.store_cache(req.message, ai_response))

            # NOTE: We are NO LONGER saving state asynchronously on every message!

            return ChatResponse(
                response=ai_response, session_id=req.session_id, hitl_pending=False
            )


chat_controller = ChatController()
chat_router = chat_controller.router
