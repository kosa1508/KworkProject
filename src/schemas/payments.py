from pydantic import BaseModel, ConfigDict
from datetime import date
"""
id:
user_id:
case_id:
price:
amount:
date:
provider:
"""


"""id:
user_id:
room_id:
date_from:
date_to:
price:
"""

class PaymentAddRequest(BaseModel):
    case_id: int
    amount: int
    date: date
    provider: str



class PaymentAdd(BaseModel):
    user_id: int
    case_id: int
    amount: int
    date: date
    provider: str
    price: int


class Payment(PaymentAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)
