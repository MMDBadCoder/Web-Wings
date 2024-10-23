from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from database.database import Base
from models.service_item import ServiceStatusForUser


class SniffEntity(Base):
    __tablename__ = "sniff"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    client_id = Column(String(100), index=True, nullable=False)
    service_id = Column(Integer, index=True, nullable=False)
    headers = Column(JSON, nullable=False)  # Assuming headers will be stored as a JSON object
    cookies = Column(Text, nullable=False)

    # Define back-population to SharedSessionEntity
    shared_sessions = relationship("SharedSessionEntity", back_populates="sniff_entity")


class SniffDto(BaseModel):
    client_id: str
    service_id: int
    headers: list
    cookies: str

    def to_entity(self):
        return SniffEntity(
            client_id=self.client_id,
            service_id=self.service_id,
            headers=self.headers,
            cookies=self.cookies
        )


class SniffResponseDto(BaseModel):
    status: ServiceStatusForUser

