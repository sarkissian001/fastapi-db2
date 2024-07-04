from fastapi import FastAPI
from fastapi_db2.api.v1 import tables
from fastapi_db2.database import Base, engine

app = FastAPI()

app.include_router(tables.router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
