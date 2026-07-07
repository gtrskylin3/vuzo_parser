from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from models.universities_directions import UniversitiesDirections
from .base import BaseRepository
from models import Users, UserDirections

class UsersRepository(BaseRepository):
    async def get_or_create_user(self, tg_id):
        result = await self.session.execute(select(Users).where(Users.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if user:
            return user
        user = Users(tg_id=tg_id)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update_user_code(self, tg_id, user_code):
        user = await self.get_or_create_user(tg_id)
        user.user_code = user_code
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user_directions_count(self, user_id: int, vuz_id : int) -> int:
        query = (
            select(func.count(UserDirections.direction_id))
            .join(
                UniversitiesDirections,
                UserDirections.direction_id == UniversitiesDirections.id
            )
            .where(
                UserDirections.user_id == user_id,
                UniversitiesDirections.university_id == vuz_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def add_direction(self, user_id: int, direction_id: int, position: int):
        vuz_query = select(UniversitiesDirections.university_id).where(
        UniversitiesDirections.id == direction_id
        )
        vuz_result = await self.session.execute(vuz_query)
        vuz_id = vuz_result.scalar_one_or_none()
        if not vuz_id:
            return False, None
        
        current_count = await self.get_user_directions_count(user_id, vuz_id)
        query = select(UserDirections).where(
            UserDirections.user_id == user_id, 
            UserDirections.direction_id == direction_id
        )
        result = await self.session.execute(query)
        user_direction = result.scalar_one_or_none()
        if user_direction:
            old_position = user_direction.user_position
            if old_position != position:
                user_direction.user_position = position
                await self.session.commit()     
            return True, old_position
        if current_count >= 5:
            return False, None  
        new_link = UserDirections(user_id=user_id, direction_id=direction_id, user_position=position)
        self.session.add(new_link)
        await self.session.commit()
        return True, None

    async def get_all_tracked_directions(self) -> list[UserDirections]:
        stmt = (select(UserDirections)
                .options(joinedload(UserDirections.user),
                joinedload(UserDirections.direction).joinedload(UniversitiesDirections.university)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    

    