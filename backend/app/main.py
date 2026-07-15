from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers.companies import router as companies_router
from app.routers.import_route import router as import_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="HSM Job Search API", lifespan=lifespan)
app.include_router(companies_router)
app.include_router(import_router)
