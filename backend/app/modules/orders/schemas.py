from pydantic import BaseModel
from typing import List, Optional


class CustomerModel(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str


class OrderItemModel(BaseModel):
    sku: str
    name: str
    category: str
    size: str
    qty: int
    price: int
    final_sale: bool
    shipped: Optional[bool] = None
    backorder_eta: Optional[str] = None


class OrderModel(BaseModel):
    order_id: str
    customer_id: str
    status: str
    placed_at: str
    delivered_at: Optional[str] = None
    expected_delivery: Optional[str] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    payment_method: str
    shipping_city: str
    items: List[OrderItemModel]
    total: int
    cancelled_at: Optional[str] = None
    refund_status: Optional[str] = None
