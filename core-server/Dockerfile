FROM python:3.10-slim

WORKDIR .

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN alembic -c alembic/alembic.ini upgrade head

CMD ["./scripts/migrate.sh", "&&","uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
