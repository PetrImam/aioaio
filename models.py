from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    role = Column(String, default="user")


class Advertisement(Base):

    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    description = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))