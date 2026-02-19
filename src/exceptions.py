from fastapi import HTTPException
from datetime import date


class BronHotelsException(Exception):
    detail = "Неожиданнаяя ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class ObjectNotFoundException(BronHotelsException):
    detail = "Объект не найден"

class ItemNotFoundException(ObjectNotFoundException):
    detail = ("Предмет не найден")

class CaseNotFoundException(ObjectNotFoundException):
    detail = "Кейс не найден"

class ObjectAlreadyExistsException(BronHotelsException):
    detail = "Похожий объект уже существует"

class AllRoomsAreBookedException(BronHotelsException):
    detail = "Не осталось свободных номеров"


class IncorrectTokenException(BronHotelsException):
    detail = "Некорректный токен"


class EmailNotRegisteredException(BronHotelsException):
    detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordException(BronHotelsException):
    detail = "Пароль неверный"


class UserAlreadyExistsException(BronHotelsException):
    detail = "Пользователь уже существует"

def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_to <= date_from:
        raise HTTPException(status_code=422, detail="Дата выезда не может быть раньше даты заезда")

class BronHotelsHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class CaseNotFoundHTTPException(BronHotelsHTTPException):
    status_code = 404
    detail = "Кейс не найден"

class ItemNotFoundHTTPException(BronHotelsHTTPException):
    status_code = 404
    detail = "Предмет не найден"

class AllRoomsAreBookedHTTPException(BronHotelsHTTPException):
    status_code = 409
    detail = "Не осталось свободных номеров"


class IncorrectTokenHTTPException(BronHotelsHTTPException):
    detail = "Некорректный токен"


class EmailNotRegisteredHTTPException(BronHotelsHTTPException):
    status_code = 401
    detail = "Пользователь с таким email не зарегистрирован"


class UserEmailAlreadyExistsHTTPException(BronHotelsHTTPException):
    status_code = 409
    detail = "Пользователь с такой почтой уже существует"


class IncorrectPasswordHTTPException(BronHotelsHTTPException):
    status_code = 401
    detail = "Пароль неверный"


class NoAccessTokenHTTPException(BronHotelsHTTPException):
    status_code = 401
    detail = "Вы не предоставили токен доступа"

class UserNotFoundException(Exception):
    """Пользователь не найден"""
    pass


class InsufficientBalanceException(Exception):
    """Недостаточно средств на балансе"""
    pass


# HTTP исключения
class UserNotFoundHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Пользователь не найден")


class InsufficientBalanceHTTPException(HTTPException):
    def __init__(self):
        super().__init__(status_code=402, detail="Недостаточно средств на балансе")