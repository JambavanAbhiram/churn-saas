from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String, unique=True, index=True, nullable=False)
    hashed_pwd = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_data  = Column(JSON)
    churn       = Column(Integer)
    probability = Column(Float)
    batch_file  = Column(String, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
