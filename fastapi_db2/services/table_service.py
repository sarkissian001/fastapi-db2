import jaydebeapi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from fastapi_db2.models.table import TableConfig
from fastapi_db2.schemas.table import TableCreate
from fastapi_db2.config import settings
import os

# Function to check if a table exists and get its schema from Db2
async def table_exists_in_db2(schema_name: str, table_name: str) -> tuple[bool, str]:
    try:
        # Ensure JAVA_HOME is set
        if not os.getenv('JAVA_HOME'):
            raise EnvironmentError("JAVA_HOME environment variable is not set")

        # Define connection parameters from settings
        db2_url = settings.DB2_URL
        db2_driver = "com.ibm.db2.jcc.DB2Driver"
        db2_jdbc_jar = "./db2jcc4.jar"  # Ensure this path is correct
        db2_user = settings.DB2_USER
        db2_password = settings.DB2_PASSWORD

        # Check if the JDBC jar file exists
        if not os.path.isfile(db2_jdbc_jar):
            raise FileNotFoundError(f"The JDBC driver jar file was not found at {db2_jdbc_jar}")

        # Establish connection
        conn = jaydebeapi.connect(db2_driver, db2_url, [db2_user, db2_password], db2_jdbc_jar)
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute(f"SELECT * FROM SYSCAT.TABLES WHERE TABSCHEMA = '{schema_name.upper()}' AND TABNAME = '{table_name.upper()}'")
        result = cursor.fetchall()

        if not result:
            return False, None

        # Fetch the schema of the table
        cursor.execute(f"SELECT COLNAME, TYPENAME FROM SYSCAT.COLUMNS WHERE TABSCHEMA = '{schema_name.upper()}' AND TABNAME = '{table_name.upper()}'")
        columns = cursor.fetchall()

        schema = ", ".join([f"{col[0]} {col[1]}" for col in columns])

        cursor.close()
        conn.close()

        return True, schema
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error occurred: {e}")

# Function to create the table configuration in PostgreSQL
async def create_table_config(db: AsyncSession, table: TableCreate):
    # Check if the table configuration already exists in PostgreSQL
    existing_table_query = await db.execute(select(TableConfig).filter_by(db2_table=table.db2_table))
    existing_table = existing_table_query.scalars().first()

    if existing_table:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table configuration already exists in PostgreSQL")

    # Split the schema and table name
    schema_name, table_name = table.db2_table.split('.')

    exists, schema = await table_exists_in_db2(schema_name, table_name)
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found in IBM Db2")

    db_table = TableConfig(db2_table=table.db2_table, schema=schema)
    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)
    return db_table
