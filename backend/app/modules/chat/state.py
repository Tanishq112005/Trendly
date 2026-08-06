from typing import TypedDict, Annotated, Sequence, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next_node: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    hitl_pending: Optional[bool]
    ticket_details: Optional[dict]
    orders: Optional[list]
    temp_extracted_email: Optional[str]
    temp_extracted_phone: Optional[str]
    temp_extracted_name: Optional[str]
    current_order_id: Optional[str]
    current_sku: Optional[str]
