from pydantic import BaseModel

class TableCreate(BaseModel):
    db2_table: str  # Format: "SCHEMA.TABLE_NAME"

class Table(BaseModel):
    id: int
    db2_table: str
    schema: str

    class Config:
        orm_mode = True
