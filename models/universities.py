from typing import List, TYPE_CHECKING

from models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models import UniversitiesDirections

class Universities(Base):
    __tablename__ = 'universities'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    directions: Mapped[List["UniversitiesDirections"]] = relationship(
        back_populates="university", 
        cascade="all, delete-orphan"
    )