FROM python:3.8-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install --no-dev

# Copy the rest of the application
COPY . /app

# Run the application
CMD ["poetry", "run", "uvicorn", "fastapi_db2.main:app", "--host", "0.0.0.0", "--port", "8000"]
