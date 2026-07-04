from typing import List, TYPE_CHECKING
from models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models import UniversitiesDirections


class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column()
    user_code: Mapped[int | None] = mapped_column()
    directions: Mapped[List["UniversitiesDirections"]] = relationship(
        secondary="user_directions", 
        back_populates="users"
    )

    