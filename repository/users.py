from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from models.universities_directions import UniversitiesDirections
from .base import BaseRepository
from models import Users, UserDirections, Universities

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
    
    async def get_user_directions_count_by_vuz(self, user_id: int, vuz_id: int) -> int:
        query = (
            select(func.count(UserDirections.direction_id))
            .join(UniversitiesDirections, UserDirections.direction_id == UniversitiesDirections.id)
            .where(UserDirections.user_id == user_id, UniversitiesDirections.vuz_id == vuz_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_user_vuz_custom_code(self, user_id: int, vuz_id: int) -> int | None:
        # Find if there's any existing direction for this user and vuz with a custom code
        query = (
            select(UserDirections.user_code)
            .join(UniversitiesDirections, UserDirections.direction_id == UniversitiesDirections.id)
            .where(UserDirections.user_id == user_id, UniversitiesDirections.vuz_id == vuz_id, UserDirections.user_code.isnot(None))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def add_direction(self, user_id: int, direction_id: int, position: int, user_code: int | None = None):
        # First, get the vuz_id for the given direction_id
        direction_obj = await self.session.get(UniversitiesDirections, direction_id)
        if not direction_obj:
            return False, None # Direction not found

        vuz_id = direction_obj.vuz_id
        
        # Now, get the count for that specific vuz
        current_count = await self.get_user_directions_count_by_vuz(user_id, vuz_id)

        query = select(UserDirections).where(
            UserDirections.user_id == user_id, 
            UserDirections.direction_id == direction_id
        )
        result = await self.session.execute(query)
        user_direction = result.scalar_one_or_none()
        
        # If user_code is not provided (e.g., user chose "use global"),
        # try to inherit custom code from another direction in the same vuz
        if user_code is None:
            user_code = await self.get_user_vuz_custom_code(user_id, vuz_id)

        if user_direction:
            old_position = user_direction.user_position
            if old_position != position or (user_code and user_direction.user_code != user_code):
                user_direction.user_position = position
                user_direction.user_code = user_code # Update with new or inherited custom code
                await self.session.commit()     
            return True, old_position
            
        if current_count >= 5:
            return False, None
              
        new_link = UserDirections(user_id=user_id, direction_id=direction_id, user_position=position, user_code=user_code)
        self.session.add(new_link)
        await self.session.commit()
        return True, None

    async def get_user_direction(self, user_id: int, direction_id: int) -> UserDirections | None:
        query = select(UserDirections).where(
            UserDirections.user_id == user_id, 
            UserDirections.direction_id == direction_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_tracked_directions(self) -> list[UserDirections]:
        stmt = (select(UserDirections)
                .options(joinedload(UserDirections.user),
                joinedload(UserDirections.direction).joinedload(UniversitiesDirections.university)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_user_codes_for_vuz(self, user_id: int, vuz_id: int, user_code: int):
        query = (
            select(UserDirections)
            .join(UniversitiesDirections, UserDirections.direction_id == UniversitiesDirections.id)
            .where(UserDirections.user_id == user_id, UniversitiesDirections.vuz_id == vuz_id)
        )
        result = await self.session.execute(query)
        directions_to_update = result.scalars().all()
        for direction in directions_to_update:
            direction.user_code = user_code
        await self.session.commit()
