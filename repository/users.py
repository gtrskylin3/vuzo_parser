from sqlalchemy import select
from .base import BaseRepository
from models import Users

class UsersRepository(BaseRepository):
    async def get_user(self, tg_id):
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
        user = await self.get_user(tg_id)
        user.user_code = user_code
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    

    
