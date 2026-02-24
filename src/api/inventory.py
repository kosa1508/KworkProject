from fastapi import APIRouter, HTTPException
from typing import List

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import ObjectNotFoundException
from src.schemas.inventory import InventoryItem, InventorySellRequest
from src.services.users import UsersService

router = APIRouter(prefix="/inventory", tags=["Инвентарь"])


@router.get("/my", response_model=List[InventoryItem])
async def get_my_inventory(
    user_id: UserIdDep,
    db: DBDep,
    limit: int = 100,
    offset: int = 0
):
    """
    Получить мой инвентарь
    """
    inventory = await UsersService(db).get_user_inventory(user_id, limit, offset)
    return inventory


@router.post("/sell/{inventory_id}")
async def sell_item(
    inventory_id: int,
    request: InventorySellRequest,
    user_id: UserIdDep,
    db: DBDep
):
    """
    Продать предмет из инвентаря
    """
    try:
        item = await UsersService(db).sell_item(user_id, inventory_id, request.price)
        return {"status": "OK", "data": item}
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))