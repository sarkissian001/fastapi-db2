from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi_db2.database import get_db
from fastapi_db2.schemas.table import Table, TableCreate
from fastapi_db2.services.table_service import create_table_config, table_exists_in_db2
from fastapi_db2.models.table import TableConfig

router = APIRouter()

@router.post("/tables/", response_model=Table)
async def add_table(table: TableCreate, db: AsyncSession = Depends(get_db)):
    return await create_table_config(db, table)

@router.get("/tables/", response_model=list[Table])
async def get_tables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TableConfig))
    tables = result.scalars().all()
    return tables

@router.get("/tables/{table_id}", response_model=Table)
async def get_table(table_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TableConfig).filter_by(id=table_id))
    table = result.scalars().first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@router.delete("/tables/{table_id}", response_model=Table)
async def delete_table(table_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TableConfig).filter_by(id=table_id))
    table = result.scalars().first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    await db.delete(table)
    await db.commit()
    return table

@router.put("/tables/{table_id}", response_model=Table)
async def update_table(table_id: int, table_update: TableCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TableConfig).filter_by(id=table_id))
    table = result.scalars().first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # Split the schema and table name
    schema_name, table_name = table_update.db2_table.split('.')

    exists, schema = await table_exists_in_db2(schema_name, table_name)
    if not exists:
        raise HTTPException(status_code=404, detail="Table not found in IBM Db2")

    table.db2_table = table_update.db2_table
    table.schema = schema

    await db.commit()
    await db.refresh(table)
    return table
