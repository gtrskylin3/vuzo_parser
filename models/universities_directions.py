from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base import Base

if TYPE_CHECKING:
    from models import Users, Universities

class UniversitiesDirections(Base):
    __tablename__ = 'universities_directions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_position: Mapped[int] = mapped_column()
    name: Mapped[str]
    url: Mapped[str]
    university_id: Mapped[int] = mapped_column(ForeignKey('universities.id', ondelete='CASCADE'))
    university: Mapped["Universities"] = relationship(back_populates="directions")
    users: Mapped[List["Users"]] = relationship(
        secondary="user_directions", 
        back_populates="directions"
    )