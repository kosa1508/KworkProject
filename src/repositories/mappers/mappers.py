from src.models import CasesOrm, ItemsOrm, PaymentsOrm
from src.models.openings import CaseOpeningsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.cases import Case
from src.schemas.items import Item
from src.schemas.openings import CaseOpeningResponse
from src.schemas.payments import Payment
from src.schemas.users import User


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User

class CaseDataMapper(DataMapper):
    db_model = CasesOrm
    schema = Case

class ItemDataMapper(DataMapper):
    db_model = ItemsOrm
    schema = Item

class PaymentDataMapper(DataMapper):
    db_model = PaymentsOrm
    schema = Payment

class CaseOpeningDataMapper(DataMapper):
    db_model = CaseOpeningsOrm
    schema = CaseOpeningResponse