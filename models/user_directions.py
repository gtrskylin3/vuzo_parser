from models import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

class UserDirections(Base):
    __tablename__ = 'user_directions'
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    direction_id: Mapped[int] = mapped_column(ForeignKey('universities_directions.id', ondelete='CASCADE'), primary_key=True) 