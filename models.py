from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import ForeignKey, BigInteger, String
from typing import List, Literal
# from database import Base

class Base(DeclarativeBase):
    pass

Languages = Literal["en", "uk", "de"]

class User(Base):
    __tablename__ = "users"
    
    id = mapped_column(primary_key=True, type_=BigInteger)
    username: Mapped[str] = mapped_column(String(length=32), unique=True, nullable=True)
    language: Mapped[Languages] = mapped_column(default='en')
