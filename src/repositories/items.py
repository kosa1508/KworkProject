from src.models import ItemsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ItemDataMapper


class ItemsRepository(BaseRepository):
    model = ItemsOrm
    mapper = ItemDataMapper