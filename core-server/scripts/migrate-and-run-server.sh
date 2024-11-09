#!/bin/bash

echo "Try to execute migrations..."
alembic -c alembic/alembic.ini upgrade head
echo "Running the application"
docker run -d --name web-wings-core --network=host web-wings:0.2

