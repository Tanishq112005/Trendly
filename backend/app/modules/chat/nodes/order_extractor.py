from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import llm
from app.modules.chat.state import AgentState

class OrderContextExtraction(BaseModel):
    extracted_order_id: Optional[str] = Field(
        None,
        description="The order ID the user is referring to in their latest message (e.g. TR-4521). If none is mentioned or implied, return null.",
    )
    extracted_sku: Optional[str] = Field(
        None,
        description="The SKU of the product the user is referring to in their latest message (e.g. TR-TSH-002). If none is mentioned, return null.",
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an extraction assistant. Analyze the user's latest message and extract any mentioned 'order ID' or 'product SKU'.\n"
            "If the user is asking a follow-up question and implies they are still talking about the previous order ID ({current_order_id}), return it.\n"
            "If no order ID or SKU is mentioned or implied, return null for both.",
        ),
        ("placeholder", "{messages}"),
    ]
)

structured_llm = llm.with_structured_output(OrderContextExtraction)

def order_extractor_node(state: AgentState) -> dict:
    """Extracts order and sku from the latest message to maintain context in the state."""
    current_order_id = state.get("current_order_id") or "None"
    
    recent_messages = state["messages"][-10:] if len(state["messages"]) > 10 else state["messages"]
    
    extraction = (prompt | structured_llm).invoke({
        "messages": recent_messages,
        "current_order_id": current_order_id
    })
    
    updates = {}
    
    # Only update state if a new ID was explicitly found or confidently implied
    if extraction.extracted_order_id:
        updates["current_order_id"] = extraction.extracted_order_id
        
    if extraction.extracted_sku:
        updates["current_sku"] = extraction.extracted_sku
        
    return updates
