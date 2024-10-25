#!/bin/bash

echo "Sleep 10 seconds to be sure that database is up!"
sleep 10
echo "Try to execute migrations..."
alembic -c alembic/alembic.ini upgrade head
echo "Running the application"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
