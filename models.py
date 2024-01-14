from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import List, Literal
from database import Base

Languages = Literal["en", "uk"]

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[int] = mapped_column(unique=True)
    language: Mapped[Languages] = mapped_column(default="en")
    words: Mapped[List["Word"]] = relationship()

class Word(Base):
    __tablename__ = "words"

    first_attempt: Mapped[str] = mapped_column(nullable=True)
    second_attempt: Mapped[str] = mapped_column(nullable=True)  
    user: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))