from contextlib import asynccontextmanager
from typing import List

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

SERVICE_INSTANCES_LIST: List[ServiceBase] = [
    IranCellService.get_instance()
]


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
    return [s.get_service_dto(client_id=client_id) for s in SERVICE_INSTANCES_LIST]


@app.post("/sniff/", response_model=SniffResponseDto)
async def sniff_packets(sniff_dto: SniffDto):
    try:
        print(f"Received sniff data from client_id: {sniff_dto.client_id}, service_id: {sniff_dto.service_id}")
        service = next((s for s in SERVICE_INSTANCES_LIST if s.service_id == sniff_dto.service_id), None)
        if service is None:
            raise HTTPException(status_code=404, detail=f"No service matched to {str(sniff_dto)}")

        if service.test_has_access(sniff_dto):
            db_client: DatabaseClient = DatabaseClient.get_instance()
            sniff_entity = sniff_dto.to_entity()
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
    shared_session_entity = db_client.create_shared_session(request)
    return shared_session_entity.session_id


@app.delete("/delete-shared-session/")
async def create_shared_session(request: SharedSessionDeleteRequestDto):
    db_client: DatabaseClient = DatabaseClient.get_instance()
    db_client.delete_session(request)


@app.get("/get-shared-session/")
async def create_shared_session(session_id: str, ):
    db_client: DatabaseClient = DatabaseClient.get_instance()
    session: SharedSessionEntity = db_client.get_session(session_id)
    sniff = session.sniff_entity
    return HeaderAndCookiesDto(headers=sniff.headers, cookies=sniff.cookies)
