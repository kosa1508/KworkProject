from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    rarity: int = Field(ge=1, le=10)
    base_price: int = Field(ge=0)
    market_price: Optional[int] = None
    weight: float = Field(ge=0.1, default=1.0)
    is_active: bool = True


class ItemCreate(ItemBase):
    case_id: int


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    rarity: Optional[int] = Field(None, ge=1, le=10)
    base_price: Optional[int] = Field(None, ge=0)
    market_price: Optional[int] = None
    weight: Optional[float] = Field(None, ge=0.1)
    is_active: Optional[bool] = None


class Item(ItemBase):
    id: int
    case_id: int
    total_opened: int
    last_opened_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ItemWithChance(Item):
    chance_percent: float  # Шанс выпадения в процентах

class ItemAdd(BaseModel):
    name: str
    case_id: int
    rarity: int
    base_price: int


class ItemAddRequest(BaseModel):
    name: str
    rarity: int
    base_price: int



class ItemPatch(BaseModel):
    name: str | None = None
    case_id: int | None = None
    rarity: int | None = None
    base_price: int | None = None


class ItemPatchRequest(BaseModel):
    name: str | None = None
    rarity: int | None = None
    base_price: int | None = None