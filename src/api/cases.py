

from fastapi import Query, APIRouter, Body, HTTPException

from src.schemas.cases import CaseAdd, CasePatch
from src.api.dependencies import PaginationDep, DBDep
from src.services.cases import CaseService


router = APIRouter(prefix="/cases", tags=["Кейсы"])


@router.get("/all_cases", summary="Получение всех кейсов")
async def get_all_cases(
    db: DBDep,
):
    return await CaseService(db).get_all_cases()



"""@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    location: str | None = Query(None, description="Локация"),
    title: str | None = Query(None, description="Название отеля"),
    date_from: date = Query(example="2024-08-01"),
    date_to: date = Query(example="2024-08-10"),
):
    hotels = await HotelService(db).get_filtered_by_time(
        pagination,
        location,
        title,
        date_from,
        date_to,
    )
    return {"status": "OK", "data": hotels}
"""

@router.get("/{case_id}", summary="Получение конкретного кейса")
async def get_case(
    case_id: int,
    db: DBDep,
):
    return await CaseService(db).get_case(case_id)



@router.put("/{case_id}", summary="Обновление данных о кейсе")
async def change_case(
    case_id: int,
    case_data: CaseAdd,
    db: DBDep,
):
    await CaseService(db).edit_case(case_id, case_data)
    return {"status": "OK"}


@router.patch("/{case_id}", summary="Частичное обновление данных об кейсе")
async def partially_edit_case(
    case_id: int,
    case_data: CasePatch,
    db: DBDep,
):
    await CaseService(db).edit_case_partially(case_id, case_data, exclude_unset=True)
    return {"status": "OK"}


@router.post("", summary="Создание кейса")
async def create_case(
    db: DBDep,
    case_data: CaseAdd = Body(
        openapi_examples={
            "1": {
                "summary": "TG",
                "value": {
                    "name": "Кейс от TG",
                    "price": 0,
                    "is_active": "True",
                    "description": "Это бонусный кейс от TG, который выдается каждому пользователю"
                },
            },
            "2": {
                "summary": "VK",
                "value": {
                    "name": "Кейс от VK",
                    "price": 10,
                    "is_active": "True",
                    "description": "Это специальный кейс от VK, который почти ничего не стоит при этом является отличным дополнением для коллекции каждого пользователя"
                },
            },
        }
    ),
):
    case = await CaseService(db).add_case(case_data)

    return {"status": "OK", "data": case}


@router.delete("/{case_id}", summary="Удаление кейса")
async def delete_case(
    case_id: int,
    db: DBDep,
):
    await CaseService(db).delete_case(case_id)
    return {"status": "OK"}
