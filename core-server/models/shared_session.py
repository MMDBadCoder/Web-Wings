from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class SharedSessionEntity(Base):
    __tablename__ = "shared_session"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    client_id = Column(String(100), index=True, nullable=False)
    session_id = Column(String(100), index=True, nullable=False)
    service_id = Column(Integer, nullable=False)
    sniff_id = Column(Integer, ForeignKey('sniff.id'), nullable=False)
    creation_time = Column(DateTime, server_default=func.now(), nullable=False)
    expiration_duration_days = Column(Integer, nullable=True)

    # Define the relationship with SniffEntity (many-to-one)
    sniff_entity = relationship("SniffEntity", back_populates="shared_sessions")


class HeaderAndCookiesDto(BaseModel):
    headers: list
    cookies: str


class SharedSessionCreationRequestDto(BaseModel):
    client_id: str
    sniff_id: int
    expiration_duration_days: int


class SharedSessionDeleteRequestDto(BaseModel):
    client_id: str
    session_id: int
