from src.repositories.mappers.base import DataMapper
from src.models import (
    UsersOrm, CasesOrm, ItemsOrm,
    CaseOpeningsOrm, UserInventoryOrm
)
from src.schemas.users import User
from src.schemas.cases import Case
from src.schemas.items import Item
from src.schemas.openings import OpeningResponse, OpeningHistoryItem
from src.schemas.inventory import InventoryItem


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User


class CaseDataMapper(DataMapper):
    db_model = CasesOrm
    schema = Case


class ItemDataMapper(DataMapper):
    db_model = ItemsOrm
    schema = Item


class CaseOpeningDataMapper(DataMapper):
    db_model = CaseOpeningsOrm
    schema = OpeningResponse


class InventoryDataMapper(DataMapper):
    db_model = UserInventoryOrm
    schema = InventoryItem