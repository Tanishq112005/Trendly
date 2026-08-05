from pydantic import BaseModel, Field
from app.core.llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from app.modules.chat.state import AgentState
from app.modules.orders.service import OrderService
from langgraph.graph import StateGraph, START, END


class ExtractionDecision(BaseModel):
    extracted_email: str = Field(
        ...,
        description="Extract the user's email address if provided in the latest message. Otherwise output exactly 'UNKNOWN'.",
    )
    extracted_phone: str = Field(
        ...,
        description="Extract the user's phone number if provided in the latest message. Otherwise output exactly 'UNKNOWN'.",
    )


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an extraction assistant. Extract the user's email and phone number from their latest message.",
        ),
        ("placeholder", "{messages}"),
    ]
)


structured_llm = llm.with_structured_output(ExtractionDecision)


def extract_node(state: AgentState) -> dict:
    extraction = (prompt | structured_llm).invoke({"messages": state["messages"]})
    return {
        "temp_extracted_email": extraction.extracted_email,
        "temp_extracted_phone": extraction.extracted_phone,
    }


def save_email_node(state: AgentState) -> dict:
    temp_email = state.get("temp_extracted_email")
    if temp_email and temp_email != "UNKNOWN":
        return {"email": temp_email}
    return {}


def save_phone_node(state: AgentState) -> dict:
    temp_phone = state.get("temp_extracted_phone")
    if temp_phone and temp_phone != "UNKNOWN":
        return {"phone": temp_phone}
    return {}


def verify_auth_node(state: AgentState) -> dict:
    email = state.get("email")
    phone = state.get("phone")
    updates = {}

    if not email and not phone:
        updates["messages"] = [
            AIMessage(
                content="To assist you better, I need to know your email and phone number first. Can you please provide me with both?"
            )
        ]
        return updates
    if not email:
        updates["messages"] = [
            AIMessage(
                content="I have your phone number, but I still need your email address to proceed. Can you please provide it?"
            )
        ]
        return updates
    if not phone:
        updates["messages"] = [
            AIMessage(
                content="I have your email, but I still need your phone number to proceed. Can you please provide it?"
            )
        ]
        return updates

    orders = OrderService.get_orders_by_customer(email, phone)
    updates["orders"] = orders

    # Save the name from the fetched orders
    if not state.get("name") and orders:
        name = orders[0].get("customer_name")
        if name:
            updates["name"] = name

    return updates


# Build the Information Agent Subgraph
info_builder = StateGraph(AgentState)
info_builder.add_node("extract", extract_node)
info_builder.add_node("save_email", save_email_node)
info_builder.add_node("save_phone", save_phone_node)
info_builder.add_node("verify", verify_auth_node)

info_builder.add_edge(START, "extract")


def route_after_extract(state: AgentState) -> list[str]:
    destinations = []

    if (
        state.get("temp_extracted_email")
        and state.get("temp_extracted_email") != "UNKNOWN"
    ):
        destinations.append("save_email")

    if (
        state.get("temp_extracted_phone")
        and state.get("temp_extracted_phone") != "UNKNOWN"
    ):
        destinations.append("save_phone")

    if not destinations:
        destinations.append("verify")

    return destinations


# Diamond routing: only send to the save nodes if data actually exists!
info_builder.add_conditional_edges(
    "extract", route_after_extract, ["save_email", "save_phone", "verify"]
)

# Fan-in to verification node
info_builder.add_edge("save_email", "verify")
info_builder.add_edge("save_phone", "verify")

info_builder.add_edge("verify", END)

information_agent_graph = info_builder.compile()
