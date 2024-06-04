#!/bin/bash

# Build Docker images for tests
docker build -f dockerfiles/Dockerfile.auth -t auth_test .
docker build -f dockerfiles/Dockerfile.authz -t authz_test .
docker build -f dockerfiles/Dockerfile.content -t content_test .

# Run Docker Compose to start the services
docker-compose up --build
