from pydantic import BaseModel, ConfigDict


class CaseAdd(BaseModel):
    name: str
    price: int
    is_active: bool
    description: str


class Case(CaseAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CasePatch(BaseModel):
    name: str | None = None
    price: int | None = None
    is_active: bool | None = None
    description: str | None = None
