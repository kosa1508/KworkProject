from fastapi import APIRouter, Body, Query, HTTPException
from datetime import date

from src.api.dependencies import DBDep
from src.exceptions import  ItemNotFoundException, \
    ItemNotFoundHTTPException, CaseNotFoundException, CaseNotFoundHTTPException
from src.schemas.items import ItemAddRequest, ItemPatchRequest
from src.services.items import ItemService


router = APIRouter(prefix="/items", tags=["Предметы инвентаря"])


@router.get("/{case_id}/items")
async def get_items(
    case_id: int,
    db: DBDep,
):
    return await ItemService(db).get_all_items(case_id)

@router.get("/{case_id}/items/{item_id}")
async def get_one_item(
    case_id: int,
    item_id: int,
    db: DBDep,
):
    try:
        return await ItemService(db).get_item(item_id, case_id)
    except ItemNotFoundException:
        raise ItemNotFoundHTTPException

@router.post("/{case_id}/items")
async def create_item(
    case_id: int,
    db: DBDep,
    item_data: ItemAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Бобер",
                "value": {
                    "name": "Бобер-курва",
                    "base_price": 10,
                    "rarity": 1,
                },
            },
            "2": {
                "summary": "Нож",
                "value": {
                    "name": "VIP нож",
                    "base_price": 1000,
                    "rarity": 5,
                },
            },
            "3": {
                "summary": "Нож_странный",
                "value": {
                    "name": "ножикс",
                    "base_price": 50,
                    "rarity": 2,
                },
            },
        }
    ),
):
    try:
        item = await ItemService(db).create_item(case_id, item_data)
    except CaseNotFoundException:
        raise CaseNotFoundHTTPException
    return {"status": "OK", "data": item}


@router.put("/{case_id}/items/{item_id}")
async def edit_item(
    case_id: int,
    item_id: int,
    item_data: ItemAddRequest,
    db: DBDep,
):

    await ItemService(db).edit_item(case_id, item_id, item_data)

    return {"status": "OK"}


@router.patch("/{case_id}/items/{item_id}")
async def partially_edit_item(
    case_id: int,
    item_id: int,
    item_data: ItemPatchRequest,
    db: DBDep,
):

    await ItemService(db).partially_edit_item(case_id, item_id, item_data)


    return {"status": "OK"}


@router.delete("/{case_id}/items/{item_id}")
async def delete_item(
    case_id: int,
    item_id: int,
    db: DBDep,
):

    await ItemService(db).delete_item(case_id, item_id)


    return {"status": "OK"}
