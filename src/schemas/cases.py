from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class CaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    image_url: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    category: Optional[str] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(CaseBase):
    name: Optional[str] = None
    price: Optional[int] = None
    is_active: Optional[bool] = None


class Case(CaseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseWithStats(Case):
    total_openings: int = 0
    total_value: int = 0
    items_count: int = 0

class CaseAdd(BaseModel):
    name: str
    price: int
    is_active: bool
    description: str


class CasePatch(BaseModel):
    name: str | None = None
    price: int | None = None
    is_active: bool | None = None
    description: str | None = None