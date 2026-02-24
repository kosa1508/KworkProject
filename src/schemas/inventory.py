from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class InventoryItem(BaseModel):
    id: int
    user_id: int
    opening_id: int
    item_id: int
    item_name: str
    item_rarity: int
    item_price: int
    is_tradable: bool
    is_sold: bool
    sold_price: Optional[int]
    sold_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventorySellRequest(BaseModel):
    inventory_id: int
    price: int