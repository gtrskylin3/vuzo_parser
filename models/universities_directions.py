from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from models.base import Base

class UniversitiesDirections(Base):
    __tablename__ = 'universities_directions'
    user_position: Mapped[int] = mapped_column()
    name: Mapped[str]
    url: Mapped[str]
    university_id: Mapped[int] = mapped_column(ForeignKey('universities.id', ondelete='CASCADE'))
    university: Mapped["Universities"] = relationship(back_populates="directions")
    users: Mapped[List["Users"]] = relationship(
        secondary="user_directions", 
        back_populates="directions"
    )