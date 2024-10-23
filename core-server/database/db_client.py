import secrets
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from models.shared_session import SharedSessionEntity, SharedSessionCreationRequestDto, SharedSessionDeleteRequestDto
from models.sniff import SniffEntity, SniffDto
from settings import DATABASE_URL

# SQLAlchemy engine and session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseClient:
    _instance = None

    def __init__(self):
        """
        Private constructor to initialize the DB connection.
        Ensures only one instance of DatabaseClient is created.
        """
        if DatabaseClient._instance is not None:
            raise Exception("This class is a singleton!")
        else:

            # Initialize the session
            self.session = SessionLocal()
            DatabaseClient._instance = self
            print(f"Connected to database")

    @staticmethod
    def get_instance():
        """
        Static method to get the singleton instance of DatabaseClient.
        If it doesn't exist, create a new one.
        """
        if DatabaseClient._instance is None:
            DatabaseClient()
        return DatabaseClient._instance

    def store_sniff_data(self, sniff_entity: SniffEntity):
        """
        Store SniffEntity in database, uniquely identified by client_id and service_id.
        """
        try:
            # Convert SniffDto to SQLAlchemy Sniff entity
            self.session.add(sniff_entity)
            self.session.commit()
            self.session.refresh(sniff_entity)  # Reload the instance with updated data
            print(f"Sniff entity for client_id={sniff_entity.client_id} "
                  f"and service_id={sniff_entity.service_id} stored successfully.")
            return sniff_entity
        except Exception as e:
            self.session.rollback()  # Rollback if there is any error
            print(f"Failed to store sniff entity: {e}")
            raise e

    def retrieve_sniff_entity(self, client_id: str, service_id: int) -> Optional[SniffDto]:
        """
        Retrieve SniffEntity from database using client_id and service_id.
        Returns None if no data is found, otherwise returns a SniffDto object.
        """
        try:
            sniff_entity = (
                self.session.query(SniffEntity)
                .filter(SniffEntity.client_id == client_id, SniffEntity.service_id == service_id)
                .first()
            )
            if sniff_entity:
                # Convert SQLAlchemy Sniff object to SniffDto
                return SniffDto(
                    client_id=sniff_entity.client_id,
                    service_id=sniff_entity.service_id,
                    headers=sniff_entity.headers,
                    cookies=sniff_entity.cookies
                )
            else:
                print(f"No entity found for client_id={client_id} and service_id={service_id}")
                return None
        except NoResultFound:
            print(f"No sniff data found for client_id={client_id} and service_id={service_id}")
            return None
        except Exception as e:
            print(f"Failed to retrieve sniff data: {e}")
            raise e

    def create_shared_session(self, creation_request: SharedSessionCreationRequestDto) -> SharedSessionEntity:
        """
        Creates a shared session for a given sniff_id and client_id.

        - Checks if a sniff entity exists with the given sniff_id, raises an exception if not.
        - Validates that the client_id matches the client_id of the sniff entity, raises an exception if not.
        - Creates a SharedSessionEntity and returns it.
        """
        client_id = creation_request.client_id
        sniff_id = creation_request.sniff_id
        try:
            # Check if the sniff entity exists
            sniff_entity = self.session.query(SniffEntity).filter(SniffEntity.id == sniff_id).first()
            if not sniff_entity:
                raise HTTPException(status_code=404, detail=f"No SniffEntity found for sniff_id={sniff_id}")

            # Check if the client_id matches the client_id of the sniff entity
            if sniff_entity.client_id != client_id:
                raise HTTPException(status_code=403,
                                    detail=f"Client ID mismatch: provided client_id={client_id}, "
                                           f"but SniffEntity has client_id={sniff_entity.client_id}")

            # Generate a random, safe session ID
            session_id = secrets.token_urlsafe(40)

            # Create a new SharedSessionEntity
            shared_session = SharedSessionEntity(
                client_id=client_id,
                session_id=session_id,
                service_id=sniff_entity.service_id,
                sniff_id=sniff_entity.id,
                expiration_duration_days=creation_request.expiration_duration_days
            )

            # Store the new session in the database
            self.session.add(shared_session)
            self.session.commit()
            self.session.refresh(shared_session)

            print(f"Shared session created with session_id={session_id} for client_id={client_id}")

            return shared_session

        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"No SniffEntity found for sniff_id={sniff_id}")
        except Exception as e:
            self.session.rollback()
            print(f"Failed to create shared session: {e}")
            raise e

    def delete_session(self, request: SharedSessionDeleteRequestDto):
        """
        Deletes a session by client_id and session_id.
        - Checks if the session exists.
        - Validates that the client_id matches the session's client_id.
        - Deletes the session if all checks pass.
        """
        try:
            # Query to find the shared session by session_id
            session = self.session.query(SharedSessionEntity).filter(
                SharedSessionEntity.session_id == request.session_id).first()

            # Check if session exists
            if session is None:
                raise HTTPException(status_code=404, detail="Session not found")

            # Check if client_id matches
            if session.client_id != request.client_id:
                raise HTTPException(status_code=403, detail="Client ID mismatch")

            # Delete the session
            self.session.delete(session)
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_session(self, session_id: str):
        """
           Get a session by session_id (passed as a query parameter).
           - Checks if the session exists.
           - Returns the session if found.
           """
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

    def close(self):
        """
        Close the database connection.
        """
        try:
            self.session.close()
            print("Database connection closed.")
        except Exception as e:
            print(f"Error occurred while closing the session: {e}")
            raise e
