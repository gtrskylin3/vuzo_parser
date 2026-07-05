from sqlalchemy import func, select

from models.user_directions import UserDirections
from models.users import Users
from .base import BaseRepository
from models import Universities, UniversitiesDirections


class UniversitiesRepository(BaseRepository):
    async def get_or_create_vuz(self, name):
        stmt = select(Universities).where(Universities.name == name)
        result = await self.session.execute(stmt)
        university = result.scalar_one_or_none()
        if university:
            return university
        university = Universities(name=name)
        self.session.add(university)
        await self.session.commit()
        await self.session.refresh(university)
        return university

    async def get_direction_by_id(self, direction_id: int) -> UniversitiesDirections | None :
        stmt = select(UniversitiesDirections).where(
            UniversitiesDirections.id == direction_id 
        )
        result = await self.session.execute(stmt)
        direction = result.scalar_one_or_none()
        if direction:
            return direction

    async def get_or_create_user_direction(
        self,
        vuz_id: int,
        position: int,
        direction_name: str,
        direction_url: str,
        user_id: int,
    ):
        stmt = (
            select(UniversitiesDirections)
            .join(UserDirections)  # Соединяем с таблицей связей
            .join(Users)  # Соединяем с пользователями
            .where(
                UniversitiesDirections.university_id == vuz_id,
                UniversitiesDirections.name == direction_name,
                Users.id == user_id,  # Фильтр по конкретному юзеру!
            )
        )
        result = await self.session.execute(stmt)
        direction = result.scalar_one_or_none()
        old_position = None
        if direction:
            old_position = direction.user_position
            direction.user_position = position
            direction.url = direction_url
        else:
            direction = UniversitiesDirections(
                university_id=vuz_id,
                user_position=position,
                name=direction_name,
                url=direction_url,
            )
            self.session.add(direction)
        await self.session.commit()
        await self.session.refresh(direction)
        return direction, old_position

    async def get_user_directions_by_vuz(self, user_id: int, vuz_name: str):
        query = (
            select(UniversitiesDirections)
            .join(Universities)
            .join(UserDirections)
            .join(Users)
            .where(Universities.name == vuz_name, Users.id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_stats(self, user_id: int):
        """
        Возвращает статистику по добавленным пользователем направлениям в разрезе ВУЗов.
        :param user_id: ID пользователя
        :return: (общее количество вузов, словарь {название_вуза: количество_направлений})
        """
        stmt = (
            select(
                Universities.name,
                func.count(UniversitiesDirections.id).label("directions_count"),
            )
            .join(UniversitiesDirections)
            .join(UserDirections)
            .where(UserDirections.user_id == user_id)
            .group_by(Universities.name)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        vuz_stats = {name: count for name, count in rows}
        total_vuz_count = len(vuz_stats)

        return total_vuz_count, vuz_stats
