import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Query
from fastapi import HTTPException
from starlette.middleware.cors import CORSMiddleware

from database.db_client import DatabaseClient
from models.service_item import ServiceDto, ServiceStatusForUser
from models.shared_session import SharedSessionCreationRequestDto, SharedSessionDeleteRequestDto, SharedSessionEntity, \
    HeaderAndCookiesDto
from models.sniff import SniffDto, SniffResponseDto
from services.iran_cell import IranCellService
from services.service_base import ServiceBase
from settings import TEST_SNIFF_AFTER_HOURS

SERVICE_INSTANCES_LIST: List[ServiceBase] = [
    IranCellService.get_instance()
]


def get_service_by_id(service_id: int):
    return next((s for s in SERVICE_INSTANCES_LIST if s.service_id == service_id), None)


# APScheduler setup
scheduler = BackgroundScheduler()


def delete_expired_sessions():
    db_client = DatabaseClient.get_instance()
    db_client.delete_expired_sessions()


scheduler.add_job(delete_expired_sessions, 'interval', minutes=60)

scheduler.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    DatabaseClient.get_instance()
    print("FastAPI app started and database client initialized.")
    yield
    db_client = DatabaseClient.get_instance()
    db_client.close()
    print("FastAPI app shutdown and database connection closed.")


app = FastAPI(lifespan=lifespan)
# Allow all origins and all methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,  # Allow cookies or authorization headers
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/services/", response_model=List[ServiceDto])
async def get_services(client_id: str = Query(..., description="Client ID")):
    db_client: DatabaseClient = DatabaseClient.get_instance()
    stored_sniff_entities = db_client.get_sniff_entities_by_client_id(client_id)
    deleting_sniff_ids = []
    added_service_ids = []
    one_hour_ago = datetime.now() - timedelta(hours=TEST_SNIFF_AFTER_HOURS)
    result = []
    for sniff in stored_sniff_entities:
        service = get_service_by_id(sniff.service_id)
        if sniff.last_tested_time < one_hour_ago and service.test_has_access(sniff):
            deleting_sniff_ids.append(sniff.id)
        else:
            result.append(service.provide_service_dto(sniff))
            added_service_ids.append(service.service_id)
    db_client.delete_sniff_entities_by_ids(deleting_sniff_ids)
    for service in SERVICE_INSTANCES_LIST:
        if not added_service_ids.__contains__(service.service_id):
            result.append(service.provide_service_dto(stored_sniff_entity=None))
    return result


@app.post("/sniff/", response_model=SniffResponseDto)
async def sniff_packets(sniff_dto: SniffDto):
    try:
        print(f"Received sniff data from client_id: {sniff_dto.client_id}, service_id: {sniff_dto.service_id}")
        service = next((s for s in SERVICE_INSTANCES_LIST if s.service_id == sniff_dto.service_id), None)
        if service is None:
            raise HTTPException(status_code=404, detail=f"No service matched to {str(sniff_dto)}")

        sniff_entity = sniff_dto.to_entity()
        if service.test_has_access(sniff_entity):
            db_client: DatabaseClient = DatabaseClient.get_instance()
            db_client.store_sniff_data(sniff_entity)
            print(f"Service {service.service_id} for client id {sniff_dto.client_id} was captured.")
            return SniffResponseDto(status=ServiceStatusForUser.captured)
        else:
            return SniffResponseDto(status=ServiceStatusForUser.sniffing)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process sniff data: {str(e)}")


@app.post("/create-shared-session/", response_model=str)
async def create_shared_session(request: SharedSessionCreationRequestDto):
    db_client: DatabaseClient = DatabaseClient.get_instance()
    all_service_ids = [s.service_id for s in SERVICE_INSTANCES_LIST]
    if not set(all_service_ids) >= set(request.service_ids):
        raise HTTPException(status_code=400, detail="Requested service ids are not valid")
    shared_session_entity = db_client.create_shared_session(request)
    return shared_session_entity.session_id


@app.delete("/delete-shared-session/")
async def delete_shared_session(request: SharedSessionDeleteRequestDto):
    db_client: DatabaseClient = DatabaseClient.get_instance()
    db_client.delete_session(request)


@app.get("/get-shared-session/", response_model=List[HeaderAndCookiesDto])
async def get_shared_session(session_id: str):
    db_client: DatabaseClient = DatabaseClient.get_instance()
    session: SharedSessionEntity = db_client.get_session(session_id)
    service_ids = json.loads(session.service_ids)
    sniff_entities = db_client.get_sniff_entities_by_client_and_services(client_id=session.client_id,
                                                                         service_ids=service_ids)
    result = []
    for sniff_entity in sniff_entities:
        result.append(HeaderAndCookiesDto(headers=sniff_entity.headers, cookies=sniff_entity.cookies,
                                          service_id=sniff_entity.service_id))
    return result
