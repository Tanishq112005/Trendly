from langchain_core.messages import SystemMessage, AIMessage
from app.core.llm import llm
from app.modules.chat.state import AgentState
from app.modules.chat.tools import OrderTools
from app.modules.chat.schemas import PrepareTicket


class ProductAgent:
    def __init__(self):
        self.llm = llm
        
        import os
        data_dir = os.path.join(os.path.dirname(__file__), "../../../../data")
        policy_file = os.path.join(data_dir, "trendly_policy.md")
        self.policy_text = ""
        if os.path.exists(policy_file):
            with open(policy_file, "r", encoding="utf-8") as f:
                self.policy_text = f.read()
                
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
        
        current_order_id = state.get("current_order_id")
        current_sku = state.get("current_sku")
        
        all_orders_summary = "No orders found."
        active_order_context = "No specific active order."
        
        if state.get("orders"):
            # Always list all order IDs
            all_orders_summary = "All User Orders: " + ", ".join([
                (getattr(o, "order_id", "") or (o.get("order_id") if isinstance(o, dict) else ""))
                for o in state.get("orders")
            ])
            
            # If there's a specific order in focus, provide its full details
            if current_order_id:
                for o in state.get("orders"):
                    if getattr(o, "order_id", None) == current_order_id or (isinstance(o, dict) and o.get("order_id") == current_order_id):
                        import json
                        order_dict = o.model_dump() if hasattr(o, "model_dump") else (o.dict() if hasattr(o, "dict") else o)
                        active_order_context = json.dumps(order_dict, indent=2)
                        break

        import datetime
        import zoneinfo
        today_date_str = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
        
        sys_msg_text = f"""You are Trendly's order assistant. You are speaking to {user_name}. Greet them by their name if you know it.

Known Customer Details (from system):
- Today's Date (Actual): {today_date_str}
- Email: {user_email}
- Phone: {user_phone}
- {all_orders_summary}
- Active Order Context:
{active_order_context}
- Active SKU Mentioned: {current_sku if current_sku else "None"}

1. If the user asks for a list of their orders or products, explicitly tell them all the orders listed above. If they ask about order status or tracking, you can use the lookup_order tool to get more details if needed.
2. IMPORTANT (Sec 1.6): ONLY if the user specifically asks about an order AND its status is 'lost_in_transit', immediately use the PrepareTicket tool. Do NOT spontaneously escalate orders when the user just asks for a general list of orders.
3. IMPORTANT (Sec 1.5): ONLY if an order's status is literally "delayed" and >3 business days past expected delivery (compared to Today's Date), offer a ₹250 store credit. Do NOT offer this if the status is "delivered", "in_transit", etc.
4. STRICT RULES: Do NOT offer unauthorized discounts. Do NOT ask for bank details.
5. ANTI-LOOP RULE: If you call a tool and it returns an error, DO NOT call the tool again. Instead, immediately ask the user for clarification or explain the error.
6. ESCALATION RULE: ONLY use the PrepareTicket tool if the user explicitly asks to talk to a human, manager, wants to initiate a return/exchange, or reports a defective product. Do NOT use PrepareTicket just because the user is angry about a delayed order. For delayed orders, follow Rule 3.
7. MEMORY RULE: You must remember the Order ID discussed in the previous turn. If the user asks a follow-up question (like "when will it arrive?"), assume they are talking about the same Order ID. Do NOT ask them to repeat the Order ID.
8. TOOL ARGUMENTS: When a tool requires 'email' and 'phone' arguments, ALWAYS use the exact Known Customer Details provided above. NEVER ask the user to provide or confirm their email or phone number if they are already known.
9. CURRENCY: All monetary values (prices, totals, shipping costs) in the order data are in Indian Rupees (INR). Always format them with the ₹ symbol (e.g., ₹899, ₹2297). Never use Dollars ($) or other currencies.
10. POLICY KNOWLEDGE: Use the Trendly Return & Exchange policy provided below to answer user queries about their products. Do not tell the user that "garments" or general apparel cannot be returned unless specifically excluded by the policy (like innerwear).

--- TRENDLY RETURN & EXCHANGE POLICY ---
{self.policy_text}
"""
        sys_msg = SystemMessage(content=sys_msg_text)
        recent_messages = state["messages"][-10:] if len(state["messages"]) > 10 else state["messages"]
        response = self.product_llm.invoke([sys_msg] + recent_messages)

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
