from sqlalchemy import func, select
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
    
    async def get_user_directions_count(self, user_id: int) -> int:
        query = select(func.count(UserDirections.direction_id)).where(UserDirections.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def add_direction(self, user_id: int, direction_id: int) -> bool:
        current_count = await self.get_user_directions_count(user_id)
        if current_count >= 5:
            return False  
        query = select(UserDirections).where(
            UserDirections.user_id == user_id, 
            UserDirections.direction_id == direction_id
        )
        exists = await self.session.execute(query)
        if exists.scalar_one_or_none():
            return True 
        new_link = UserDirections(user_id=user_id, direction_id=direction_id)
        self.session.add(new_link)
        await self.session.commit()
        return True

    async def get_all_directions(self):
        pass
