import json
from datetime import datetime
from langchain_core.tools import tool
from app.modules.orders.service import OrderService
from app.core.database import db_manager


class OrderTools:
    SIMULATED_CURRENT_DATE = datetime.fromisoformat("2026-08-05T00:00:00+00:00")

    @staticmethod
    @tool
    def lookup_order(order_id: str, email: str, phone: str) -> str:
        """Look up the details of an order using the known customer email and phone."""
        if not OrderService.verify_customer_identity(order_id, email, phone):
            return "Error: Verification failed. The provided email and phone do not match the order records."
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return "Error: Order not found."
        return json.dumps(order, indent=2)

    @staticmethod
    @tool
    def list_user_orders(email: str, phone: str) -> str:
        """Fetch all orders associated with a user using their known email and phone."""
        orders = OrderService.get_orders_by_customer(email, phone)
        if not orders:
            return "No orders found for this email and phone number."

        # We only return high-level details to save tokens
        summary = []
        for o in orders:
            item_names = ", ".join(
                [item.get("name", "Unknown Item") for item in o.get("items", [])]
            )
            summary.append(
                f"Order ID: {o.get('order_id')} | Status: {o.get('status')} | Items: {item_names}"
            )
        return "\n".join(summary)

    @staticmethod
    @tool
    def check_return_eligibility(order_id: str, email: str, phone: str) -> str:
        """Check if an order is eligible for a return or exchange based on the 30-day window and item categories using the known customer email and phone."""
        if not OrderService.verify_customer_identity(order_id, email, phone):
            return (
                "Error: Verification failed. The provided email and phone do not match."
            )

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

        non_returnable = [
            "innerwear",
            "jewellery",
            "beauty",
            "fragrance",
            "face masks",
            "gift cards",
        ]
        report = [
            f"Order delivered {days_since_delivery} days ago. Within 30-day window."
        ]
        for item in order.get("items", []):
            cat = item.get("category", "").lower()
            if cat in non_returnable:
                report.append(
                    f"- {item['name']}: NOT ELIGIBLE (Non-returnable category: '{cat}')."
                )
            elif item.get("final_sale"):
                report.append(
                    f"- {item['name']}: ELIGIBLE FOR SIZE EXCHANGE ONLY (Final sale item)."
                )
            else:
                report.append(f"- {item['name']}: ELIGIBLE for return or exchange.")

        return "\n".join(report)


class TicketTools:
    @staticmethod
    @tool
    def escalate_to_human(
        session_id: str, order_id: str, reason: str, summary: str
    ) -> str:
        """Escalate the conversation to a human support agent."""
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets (session_id, summary) VALUES (?, ?)",
            (session_id, f"Order: {order_id} | Reason: {reason} | Summary: {summary}"),
        )
        conn.commit()
        conn.close()
        return "SUCCESS: Ticket created."
