from sqlalchemy import select
from .base import BaseRepository
from models import Universities, UniversitiesDirections

class UniversitiesRepository(BaseRepository):
    async def get_or_create_vuz(self, name):
        stmt = select(Universities).where(Universities.name==name)
        result = await self.session.execute(stmt)
        university = result.scalar_one_or_none()
        if university:
            return university
        university = Universities(name=name)
        self.session.add(university)
        await self.session.commit()
        await self.session.refresh(university)
        return university
    
    async def get_or_create_direction(self, vuz_id: int, position: int, direction_name: str, direction_url: str) -> UniversitiesDirections:
        stmt = select(UniversitiesDirections).where(
            UniversitiesDirections.university_id == vuz_id,
            UniversitiesDirections.name == direction_name,
            UniversitiesDirections.user_position == position,
            UniversitiesDirections.url == direction_url
        )
        result = await self.session.execute(stmt)
        direction = result.scalar_one_or_none()
        if direction:
            return direction
        direction = UniversitiesDirections(university_id=vuz_id, user_position = position, name=direction_name, url=direction_url)
        self.session.add(direction)
        await self.session.commit()
        await self.session.refresh(direction)
        return direction
    
    
    