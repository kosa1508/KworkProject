from pydantic import BaseModel, ConfigDict



"""id
name
case_id
rarity
base_price"""

class ItemAdd(BaseModel):
    name: str
    case_id: int
    rarity: int
    base_price: int


class ItemAddRequest(BaseModel):
    name: str
    rarity: int
    base_price: int


class Item(ItemAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ItemPatch(BaseModel):
    name: str | None = None
    case_id: int | None = None
    rarity: int | None = None
    base_price: int | None = None


class ItemPatchRequest(BaseModel):
    name: str | None = None
    rarity: int | None = None
    base_price: int | None = None
