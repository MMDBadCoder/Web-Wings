#!/bin/bash

sleep 5
alembic -c alembic/alembic.ini upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
