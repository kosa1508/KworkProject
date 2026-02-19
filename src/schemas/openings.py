from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CaseOpeningRequest(BaseModel):
    case_id: int


class CaseOpeningResponse(BaseModel):
    id: int
    user_id: int
    case_id: int
    item_id: int
    item_name: str
    item_rarity: int
    item_price: int
    server_seed: str
    client_seed: str
    nonce: int
    roll: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpeningHistoryResponse(BaseModel):
    id: int
    case_name: str
    item_name: str
    item_rarity: int
    item_price: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerifyOpeningRequest(BaseModel):
    opening_id: int
    server_seed: str
    client_seed: str
    nonce: int
    roll: int


class VerifyOpeningResponse(BaseModel):
    is_valid: bool
    expected_roll: int
    expected_item: Optional[dict] = None