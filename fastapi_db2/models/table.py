from sqlalchemy import Column, Integer, String
from fastapi_db2.database import Base

class TableConfig(Base):
    __tablename__ = "table_configs"

    id = Column(Integer, primary_key=True, index=True)
    db2_table = Column(String, index=True)
    schema = Column(String)
