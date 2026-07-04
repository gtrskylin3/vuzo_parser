from typing import List

from models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Universities(Base):
    __tablename__ = 'universities'
    name: Mapped[str] = mapped_column()
    directions: Mapped[List["UniversitiesDirections"]] = relationship(
        back_populates="university", 
        cascade="all, delete-orphan"
    )