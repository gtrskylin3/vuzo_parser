from typing import TYPE_CHECKING

from models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from models import UniversitiesDirections, Users

class UserDirections(Base):
    __tablename__ = 'user_directions'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    direction_id: Mapped[int] = mapped_column(ForeignKey('universities_directions.id', ondelete='CASCADE'), primary_key=True) 
    user_position: Mapped[int | None] = mapped_column()
    user: Mapped["Users"] = relationship(back_populates="user_directions_links")
    direction: Mapped["UniversitiesDirections"] = relationship(back_populates="user_directions_links")