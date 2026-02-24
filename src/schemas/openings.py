from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from src.schemas.items import ItemWithChance


class OpeningRequest(BaseModel):
    case_id: int
    idempotency_key: str = Field(..., min_length=32, max_length=64)


class OpeningResponse(BaseModel):
    id: int
    case_id: int
    item_id: int
    item_name: str
    item_rarity: int
    item_price: int
    roll: int
    server_seed_hash: str
    client_seed: str
    nonce: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpeningVerifyRequest(BaseModel):
    opening_id: int
    server_seed: str
    client_seed: str
    nonce: int
    roll: int


class OpeningVerifyResponse(BaseModel):
    is_valid: bool
    expected_roll: int
    expected_item: Optional[dict] = None


class OpeningHistoryItem(BaseModel):
    id: int
    case_name: str
    item_name: str
    item_rarity: int
    item_price: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseContents(BaseModel):
    case_id: int
    case_name: str
    items: List[ItemWithChance]
    total_value: int
    avg_price: float