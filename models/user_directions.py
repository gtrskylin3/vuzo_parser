from models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.users import Users
    from models.universities_directions import UniversitiesDirections

class UserDirections(Base):
    __tablename__ = 'user_directions'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    direction_id: Mapped[int] = mapped_column(ForeignKey('universities_directions.id', ondelete='CASCADE'), primary_key=True)
    user_position: Mapped[int | None] = mapped_column(nullable=True)
    user_code: Mapped[int | None] = mapped_column(nullable=True)

    # Связи, которые "смотрят" из этой таблицы на другие
    user: Mapped["Users"] = relationship(back_populates="directions_links")
    direction: Mapped["UniversitiesDirections"] = relationship(back_populates="user_links")
