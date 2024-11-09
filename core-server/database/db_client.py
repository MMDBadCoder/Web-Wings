import json
import secrets
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from models.shared_session import SharedSessionEntity, SharedSessionCreationRequestDto
from models.sniff import SniffEntity
from settings import DATABASE_URL

# SQLAlchemy engine and session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseClient:
    _instance = None

    def __init__(self):
        if DatabaseClient._instance is not None:
            raise Exception("This class is a singleton!")
        else:

            # Initialize the session
            self.session = SessionLocal()
            DatabaseClient._instance = self
            print(f"Connected to database")

    @staticmethod
    def get_instance():
        if DatabaseClient._instance is None:
            DatabaseClient()
        return DatabaseClient._instance

    def store_sniff_data(self, sniff_entity: SniffEntity):
        try:
            # Convert SniffDto to SQLAlchemy Sniff entity
            self.session.add(sniff_entity)
            self.session.query(SniffEntity).filter(
                SniffEntity.service_id == sniff_entity.service_id,
                SniffEntity.client_id == sniff_entity.client_id
            ).delete(synchronize_session=False)
            self.session.commit()
            print(f"Sniff entity for client_id={sniff_entity.client_id} "
                  f"and service_id={sniff_entity.service_id} stored successfully.")
            return sniff_entity
        except Exception as e:
            self.session.rollback()  # Rollback if there is any error
            print(f"Failed to store sniff entity: {e}")
            raise e

    def get_sniff_entities_by_client_id(self, client_id: str) -> List[SniffEntity]:
        try:
            return self.session.query(SniffEntity).filter(SniffEntity.client_id == client_id).all()
        except Exception as e:
            print(f"Error occurred while fetching sniff entities: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def update_last_tested_time(self, sniff_id: int):
        try:
            sniff_entity = self.session.query(SniffEntity).filter(SniffEntity.id == sniff_id).first()
            sniff_entity.last_tested_time = func.now()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error occurred while updating last_tested_time: {e}")
            raise e

    def delete_sniff_entities_by_ids(self, sniff_ids: list[int]):
        try:
            self.session.query(SniffEntity).filter(SniffEntity.id.in_(sniff_ids)).delete(synchronize_session=False)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error occurred while deleting sniff entities: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def create_shared_session(self, creation_request: SharedSessionCreationRequestDto) -> SharedSessionEntity:
        client_id = creation_request.client_id
        try:
            # Generate a random, safe session ID
            session_id = secrets.token_urlsafe(40)

            # Create a new SharedSessionEntity
            expiration_time = datetime.now() + timedelta(days=creation_request.expiration_duration_days)
            shared_session = SharedSessionEntity(
                client_id=client_id,
                title=creation_request.title,
                service_ids=json.dumps(creation_request.service_ids),
                session_id=session_id,
                expiration_duration_days=creation_request.expiration_duration_days,
                expiration_time=expiration_time
            )

            # Store the new session in the database
            self.session.add(shared_session)
            self.session.commit()
            self.session.refresh(shared_session)

            print(f"Shared session created with session_id={session_id} for client_id={client_id}")

            return shared_session

        except Exception as e:
            self.session.rollback()
            print(f"Failed to create shared session: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def delete_session(self, client_id: str, session_id: str):
        try:
            self.session.query(SharedSessionEntity).filter(
                SharedSessionEntity.session_id == session_id,
                SharedSessionEntity.client_id == client_id
            ).delete(synchronize_session=False)
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_session(self, session_id: str):
        try:
            # Query the session by session_id
            session = self.session.query(SharedSessionEntity).filter(
                SharedSessionEntity.session_id == session_id).first()

            # Check if the session exists
            if session is None:
                raise HTTPException(status_code=404, detail="Session not found")

            return session

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_sniff_entities_by_client_and_services(self, client_id: str, service_ids: list[int]):
        try:
            return self.session.query(SniffEntity).filter(
                SniffEntity.client_id == client_id,
                SniffEntity.service_id.in_(service_ids)
            ).all()
        except Exception as e:
            print(f"Error occurred while fetching sniff entities: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def delete_expired_sessions(self):
        try:
            current_time = datetime.now()
            self.session.query(SharedSessionEntity).filter(SharedSessionEntity.expiration_time < current_time).delete(
                synchronize_session=False)
            self.session.commit()
            print(f"Deleted expired sessions at {current_time}")
        except Exception as e:
            self.session.rollback()
            print(f"Error occurred while deleting expired sessions: {e}")
        finally:
            self.session.close()

    def get_sessions_by_client_id(self, client_id: str) -> List[SharedSessionEntity]:
        """
        Retrieves a list of SharedSessionEntity records that match the given client_id.
        """
        try:
            return self.session.query(SharedSessionEntity).filter(
                SharedSessionEntity.client_id == client_id
            ).all()
        except Exception as e:
            print(f"Error occurred while fetching sessions: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def close(self):
        try:
            self.session.close()
            print("Database connection closed.")
        except Exception as e:
            print(f"Error occurred while closing the session: {e}")
            raise e
