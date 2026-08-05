import json
import os
from typing import Dict, Any, Optional

class OrderService:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../data")
    ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
    
    @classmethod
    def load_orders_data(cls) -> Dict[str, Any]:
        with open(cls.ORDERS_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def get_order_by_id(cls, order_id: str) -> Optional[Dict[str, Any]]:
        data = cls.load_orders_data()
        for order in data.get("orders", []):
            if order.get("order_id") == order_id:
                return order
        return None

    @classmethod
    def verify_customer_identity(cls, order_id: str, email_or_phone: str) -> bool:
        order = cls.get_order_by_id(order_id)
        if not order:
            return False
            
        customer_id = order.get("customer_id")
        data = cls.load_orders_data()
        
        for customer in data.get("customers", []):
            if customer.get("customer_id") == customer_id:
                email = customer.get("email", "").lower().strip()
                phone = customer.get("phone", "").strip()
                query = email_or_phone.lower().strip()
                
                if query == email or query == phone:
                    return True
        return False
