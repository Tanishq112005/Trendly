import json
import os
from typing import Dict, Any, Optional, List
from app.modules.orders.schemas import OrderModel


class OrderService:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../data")
    ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

    @classmethod
    def load_orders_data(cls) -> Dict[str, Any]:
        with open(cls.ORDERS_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def get_order_by_id(cls, order_id: str) -> Optional[OrderModel]:
        data = cls.load_orders_data()
        for order in data.get("orders", []):
            if order.get("order_id") == order_id:
                return OrderModel(**order)
        return None

    @classmethod
    def verify_customer_identity(cls, order_id: str, email: str, phone: str) -> bool:
        data = cls.load_orders_data()
        
        target_customer_id = None
        for order in data.get("orders", []):
            if order.get("order_id") == order_id:
                target_customer_id = order.get("customer_id")
                break
                
        if not target_customer_id:
            return False

        for customer in data.get("customers", []):
            if customer.get("customer_id") == target_customer_id:
                c_email = customer.get("email", "").lower().strip()
                c_phone = customer.get("phone", "").strip()

                if email.lower().strip() == c_email and phone.strip() == c_phone:
                    return True
        return False

    @classmethod
    def get_orders_by_customer(cls, email: str, phone: str) -> List[OrderModel]:
        data = cls.load_orders_data()
        target_customer_id = None

        for customer in data.get("customers", []):
            c_email = customer.get("email", "").lower().strip()
            c_phone = customer.get("phone", "").strip()
            if email.lower().strip() == c_email and phone.strip() == c_phone:
                target_customer_id = customer.get("customer_id")
                break

        if not target_customer_id:
            return []

        customer_orders = []
        for order in data.get("orders", []):
            if order.get("customer_id") == target_customer_id:
                customer_orders.append(OrderModel(**order))

        return customer_orders

    @classmethod
    def get_customer_name(cls, email: str, phone: str) -> Optional[str]:
        data = cls.load_orders_data()
        for customer in data.get("customers", []):
            c_email = customer.get("email", "").lower().strip()
            c_phone = customer.get("phone", "").strip()
            if email.lower().strip() == c_email and phone.strip() == c_phone:
                return customer.get("name")
        return None
