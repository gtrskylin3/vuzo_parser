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

    async def get_direction_by_id(self, direction_id: int) -> UniversitiesDirections | None:
        stmt = select(UniversitiesDirections).where(
            UniversitiesDirections.id == direction_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_direction(
        self,
        vuz_id: int,
        direction_name: str,
        direction_url: str,
    ) -> UniversitiesDirections:
        """Находит или создает направление (без привязки к пользователю)."""
        stmt = select(UniversitiesDirections).where(
            UniversitiesDirections.university_id == vuz_id,
            UniversitiesDirections.url == direction_url,
            UniversitiesDirections.name == direction_name,
        )
        result = await self.session.execute(stmt)
        direction = result.scalar_one_or_none()

        if direction:
            return direction

        # Если не нашли - создаем новое
        new_direction = UniversitiesDirections(
            university_id=vuz_id,
            name=direction_name,
            url=direction_url,
        )
        self.session.add(new_direction)
        await self.session.commit()
        await self.session.refresh(new_direction)
        return new_direction

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
