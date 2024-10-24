from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from sqlalchemy import Text

from database.database import Base
from models.service_item import ServiceStatusForUser


class SniffEntity(Base):
    __tablename__ = "sniff"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    client_id = Column(String(100), index=True, nullable=False)
    service_id = Column(Integer, index=True, nullable=False)
    headers = Column(JSON, nullable=False)  # Assuming headers will be stored as a JSON object
    cookies = Column(Text, nullable=False)
    last_tested_time = Column(DateTime, server_default=func.now(), nullable=False)


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
