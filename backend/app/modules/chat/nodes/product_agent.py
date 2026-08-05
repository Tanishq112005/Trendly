from langchain_core.messages import SystemMessage, AIMessage
from app.core.llm import llm
from app.modules.chat.state import AgentState
from app.modules.chat.tools import OrderTools
from app.modules.chat.nodes.ticket_agent import PrepareTicket


class ProductAgent:
    def __init__(self):
        self.llm = llm
        # Use PrepareTicket so we can intercept and ask for user confirmation
        self.tools = [
            OrderTools.lookup_order,
            OrderTools.check_return_eligibility,
            OrderTools.list_user_orders,
            PrepareTicket,
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
- Phone: {user_phone}
- orderlist : {orders_info}

1. If the user asks for a list of their orders or products, explicitly tell them all the orders listed above. If they ask about order status or tracking, you can use the lookup_order tool to get more details if needed.
2. IMPORTANT (Sec 1.6): If an order is 'lost_in_transit', immediately use the PrepareTicket tool. Do NOT process a return.
3. IMPORTANT (Sec 1.5): ONLY if an order's status is literally "delayed" and >3 business days past expected delivery, offer a ₹250 store credit. Do NOT offer this if the status is "delivered", "in_transit", etc.
4. STRICT RULES: Do NOT offer unauthorized discounts. Do NOT ask for bank details.
5. ANTI-LOOP RULE: If you call a tool and it returns an error, DO NOT call the tool again. Instead, immediately ask the user for clarification or explain the error.
6. If the user reports a defective product or explicitly demands escalation, use the PrepareTicket tool.
Be polite and concise."""
        sys_msg = SystemMessage(content=sys_msg_text)
        response = self.product_llm.invoke([sys_msg] + state["messages"])
        
        # Intercept PrepareTicket tool call for HITL confirmation
        if response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "PrepareTicket":
                    hitl_msg = AIMessage(
                        content="I have prepared the ticket for your issue. Please confirm if you'd like me to create it."
                    )
                    return {
                        "messages": [hitl_msg],
                        "hitl_pending": True,
                        "ticket_details": tool_call["args"],
                    }

        return {"messages": [response], "hitl_pending": False}


product_agent_instance = ProductAgent()
