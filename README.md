### RUN Application 

```shell
poetry run uvicorn fastapi_db2.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Migrations

```shell
poetry run alembic upgrade head
```



### Run Locally With Shell

```shell
./run
```
