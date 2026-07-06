from typing import List, TYPE_CHECKING
from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.user_directions import UserDirections

class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column()
    user_code: Mapped[int | None] = mapped_column()

    directions_links: Mapped[List["UserDirections"]] = relationship(back_populates="user")
