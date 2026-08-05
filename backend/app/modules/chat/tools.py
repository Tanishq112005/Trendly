import json
from datetime import datetime, timezone
from langchain_core.tools import tool
from app.modules.orders.service import OrderService
from app.core.database import db_manager

# Note: Using a fixed simulated 'current date' of Aug 5, 2026 to match the assignment's context
SIMULATED_CURRENT_DATE = datetime.fromisoformat("2026-08-05T00:00:00+00:00")

@tool
def lookup_order(order_id: str, email_or_phone: str) -> str:
    """
    Look up the details of an order. 
    You MUST ask the user for their email or phone number before calling this tool to verify their identity.
    Do NOT call this tool if the user hasn't provided their email or phone.
    """
    if not OrderService.verify_customer_identity(order_id, email_or_phone):
        return "Error: Verification failed. The provided email or phone does not match the order records. Ask the user to verify again."
    
    order = OrderService.get_order_by_id(order_id)
    if not order:
        return "Error: Order not found."
    
    return json.dumps(order, indent=2)


@tool
def check_return_eligibility(order_id: str, email_or_phone: str) -> str:
    """
    Check if an order is eligible for a return or exchange based on the 30-day window and item categories.
    You MUST ask the user for their email or phone number before calling this tool to verify their identity.
    """
    if not OrderService.verify_customer_identity(order_id, email_or_phone):
        return "Error: Verification failed. The provided email or phone does not match the order records."

    order = OrderService.get_order_by_id(order_id)
    if not order:
        return "Error: Order not found."

    if order.get("status") == "cancelled":
        return "Order was cancelled. No return can be raised per section 2.6."

    delivered_at_str = order.get("delivered_at")
    if not delivered_at_str:
        return f"Order has not been delivered yet. Current status: {order.get('status')}. Returns are only possible after delivery."

    # Parse delivery date (replace Z with +00:00 for python 3.10 compatibility)
    delivered_at_str = delivered_at_str.replace("Z", "+00:00")
    delivered_at = datetime.fromisoformat(delivered_at_str)
    
    days_since_delivery = (SIMULATED_CURRENT_DATE - delivered_at).days

    if days_since_delivery > 30:
        return f"NOT ELIGIBLE: The order was delivered {days_since_delivery} days ago on {delivered_at.strftime('%Y-%m-%d')}. The 30-day return window has expired (Section 2.1). You MUST refuse the return."

    # Check categories
    non_returnable = ["innerwear", "jewellery", "beauty", "fragrance", "face masks", "gift cards"]
    
    report = []
    report.append(f"Order delivered {days_since_delivery} days ago. Within 30-day window.")
    for item in order.get("items", []):
        cat = item.get("category", "").lower()
        if cat in non_returnable:
            report.append(f"- {item['name']} (SKU: {item['sku']}): NOT ELIGIBLE (Non-returnable category: '{cat}' per section 2.3).")
        elif item.get("final_sale"):
            report.append(f"- {item['name']} (SKU: {item['sku']}): ELIGIBLE FOR SIZE EXCHANGE ONLY (Final sale item per section 2.4). No refunds.")
        else:
            report.append(f"- {item['name']} (SKU: {item['sku']}): ELIGIBLE for return or exchange.")

    return "\n".join(report)


@tool
def escalate_to_human(session_id: str, order_id: str, reason: str, summary: str) -> str:
    """
    Escalate the conversation to a human support agent.
    Use this for edge cases like lost parcels, second exchange requests, COD refund bank details, or if the user demands a human.
    """
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (session_id, summary) VALUES (?, ?)",
        (session_id, f"Order: {order_id} | Reason: {reason} | Summary: {summary}")
    )
    conn.commit()
    conn.close()
    
    return "SUCCESS: Ticket created. Inform the user you have escalated the issue to the human support team and they will receive an email shortly."
