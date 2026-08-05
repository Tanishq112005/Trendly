from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from app.core.config import GROQ_API_KEY
from app.modules.chat.state import AgentState
from app.modules.chat.tools import OrderTools, TicketTools


class ProductAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0
        )
        # Added TicketTools so the ProductAgent can escalate lost parcels directly
        self.tools = [
            OrderTools.lookup_order,
            OrderTools.check_return_eligibility,
            OrderTools.list_user_orders,
            TicketTools.escalate_to_human,
        ]
        self.product_llm = self.llm.bind_tools(self.tools)

    def invoke(self, state: AgentState) -> dict:
        """Handles orders and returns using tools."""
        sys_msg = SystemMessage(content="""You are Trendly's order assistant. 
1. You MUST ask the user for BOTH their email AND their phone number before executing any tools. If they only give one, ask for the other.
2. If the user asks for a list of all their orders, use the list_user_orders tool. When you receive the list of orders from the tool, you MUST explicitly output all of them to the user.
2. IMPORTANT (Sec 1.6): If an order is 'lost_in_transit', you must immediately use the escalate_to_human tool. Do NOT attempt to process a return for it.
3. IMPORTANT (Sec 1.5): ONLY if an order's status is literally "delayed" and it is >3 business days past its expected delivery, you may inform the user about a ₹250 store credit. Do NOT offer this if the status is "delivered", "in_transit", or anything else.
4. STRICT RULES: Do NOT offer unauthorized discounts. Do NOT ask for or collect bank details or card numbers. Do NOT confirm orders belonging to a different customer.
Be polite and concise.""")
        response = self.product_llm.invoke([sys_msg] + state["messages"])
        return {"messages": [response]}


product_agent_instance = ProductAgent()
