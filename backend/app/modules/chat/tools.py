import json
from datetime import datetime
from langchain_core.tools import tool
from app.modules.orders.service import OrderService
from app.core.database import db_manager

class OrderTools:
    SIMULATED_CURRENT_DATE = datetime.fromisoformat("2026-08-05T00:00:00+00:00")

    @staticmethod
    @tool
    def lookup_order(order_id: str, email_or_phone: str) -> str:
        """Look up the details of an order. You MUST ask the user for their email or phone number first."""
        if not OrderService.verify_customer_identity(order_id, email_or_phone):
            return "Error: Verification failed. The provided email or phone does not match the order records."
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return "Error: Order not found."
        return json.dumps(order, indent=2)

    @staticmethod
    @tool
    def check_return_eligibility(order_id: str, email_or_phone: str) -> str:
        """Check if an order is eligible for a return or exchange based on the 30-day window and item categories."""
        if not OrderService.verify_customer_identity(order_id, email_or_phone):
            return "Error: Verification failed. The provided email or phone does not match."
        
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return "Error: Order not found."
        
        if order.get("status") == "cancelled":
            return "Order was cancelled. No return can be raised."
            
        delivered_at_str = order.get("delivered_at")
        if not delivered_at_str:
            return f"Order has not been delivered yet. Current status: {order.get('status')}."

        delivered_at_str = delivered_at_str.replace("Z", "+00:00")
        delivered_at = datetime.fromisoformat(delivered_at_str)
        days_since_delivery = (OrderTools.SIMULATED_CURRENT_DATE - delivered_at).days

        if days_since_delivery > 30:
            return f"NOT ELIGIBLE: Delivered {days_since_delivery} days ago. 30-day window expired."

        non_returnable = ["innerwear", "jewellery", "beauty", "fragrance", "face masks", "gift cards"]
        report = [f"Order delivered {days_since_delivery} days ago. Within 30-day window."]
        for item in order.get("items", []):
            cat = item.get("category", "").lower()
            if cat in non_returnable:
                report.append(f"- {item['name']}: NOT ELIGIBLE (Non-returnable category: '{cat}').")
            elif item.get("final_sale"):
                report.append(f"- {item['name']}: ELIGIBLE FOR SIZE EXCHANGE ONLY (Final sale item).")
            else:
                report.append(f"- {item['name']}: ELIGIBLE for return or exchange.")
        
        return "\n".join(report)

class TicketTools:
    @staticmethod
    @tool
    def escalate_to_human(session_id: str, order_id: str, reason: str, summary: str) -> str:
        """Escalate the conversation to a human support agent."""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets (session_id, summary) VALUES (?, ?)",
            (session_id, f"Order: {order_id} | Reason: {reason} | Summary: {summary}")
        )
        conn.commit()
        conn.close()
        return "SUCCESS: Ticket created."
