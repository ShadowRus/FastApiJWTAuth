from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
import hashlib

from fastapi import FastAPI

SQLALCHEMY_DATABASE_URL = "sqlite:///./user.db"

# создание движка
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base = declarative_base()


class Users(Base):
    __tablename__ = "USERINFO"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String, )

SessionLocal = sessionmaker(autoflush=False, bind=engine)