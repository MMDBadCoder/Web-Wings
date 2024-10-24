from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, JSON, func

from database.database import Base


class SharedSessionEntity(Base):
    __tablename__ = "shared_session"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    client_id = Column(String(100), index=True, nullable=False)
    session_id = Column(String(100), index=True, nullable=False)

    # Storing service_ids as a list of integers using JSON column
    service_ids = Column(JSON, nullable=False)

    creation_time = Column(DateTime, server_default=func.now(), nullable=False)
    expiration_duration_days = Column(Integer, nullable=True)
    expiration_time = Column(DateTime, nullable=False)


class HeaderAndCookiesDto(BaseModel):
    service_id: int
    headers: list
    cookies: str


class SharedSessionCreationRequestDto(BaseModel):
    client_id: str
    service_ids: List[int]
    expiration_duration_days: int


class SharedSessionDeleteRequestDto(BaseModel):
    client_id: str
    session_id: int
