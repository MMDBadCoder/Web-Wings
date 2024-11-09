#!/bin/bash

echo "Sleep 10 seconds to be sure that database is up!"
sleep 10
echo "Try to execute migrations..."
alembic -c alembic/alembic.ini upgrade head
echo "Running the application"
docker run -d --name web-wings-core --network=host web-wings:0.2

