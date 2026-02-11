from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SnakeLogin(Base):
    __tablename__ = "snake_logins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(20), nullable=False)
    filename = Column(String(255))
    mime_type = Column(String(100))
    image_bytes = Column(LargeBinary)
    width = Column(Integer)
    height = Column(Integer)
    text_content = Column(Text)
    text_length = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SnakeGameScore(Base):
    __tablename__ = "snake_game_scores"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
