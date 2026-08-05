from langchain_core.messages import SystemMessage
from app.core.llm import llm
from app.modules.chat.state import AgentState
from app.modules.chat.tools import OrderTools, TicketTools


class ProductAgent:
    def __init__(self):
        self.llm = llm
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
        user_name = state.get("name") or "the customer"
        user_email = state.get("email") or "Unknown"
        user_phone = state.get("phone") or "Unknown"

        orders_info = ""
        if state.get("orders"):
            orders_info = "\nCustomer's Orders:\n"
            for o in state.get("orders"):
                orders_info += f"- Order ID: {o.get('order_id')}, Status: {o.get('status')}, Expected: {o.get('expected_delivery')}, Items: {', '.join([i.get('name', 'Unknown') for i in o.get('items', [])])}\n"

        sys_msg_text = f"""You are Trendly's order assistant. You are speaking to {user_name}. Greet them by their name if you know it.

Known Customer Details (from system):
- Email: {user_email}
- Phone: {user_phone}{orders_info}

1. If the user asks for a list of their orders or products, explicitly tell them all the orders listed above. If they ask about order status or tracking, you can use the lookup_order tool to get more details if needed.
2. IMPORTANT (Sec 1.6): If an order is 'lost_in_transit', immediately use the escalate_to_human tool. Do NOT process a return.
3. IMPORTANT (Sec 1.5): ONLY if an order's status is literally "delayed" and >3 business days past expected delivery, offer a ₹250 store credit. Do NOT offer this if the status is "delivered", "in_transit", etc.
4. STRICT RULES: Do NOT offer unauthorized discounts. Do NOT ask for bank details.
5. ANTI-LOOP RULE: If you call a tool and it returns an error, DO NOT call the tool again. Instead, immediately ask the user for clarification or explain the error.
Be polite and concise."""
        sys_msg = SystemMessage(content=sys_msg_text)
        response = self.product_llm.invoke([sys_msg] + state["messages"])
        return {"messages": [response]}


product_agent_instance = ProductAgent()
