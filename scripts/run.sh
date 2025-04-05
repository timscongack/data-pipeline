#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
for cmd in docker docker-compose python; do
    if ! command_exists $cmd; then
        echo "Error: $cmd is required but not installed."
        exit 1
    fi
done

# Create necessary directories
mkdir -p docker/trino/catalog
mkdir -p volume

# Build and start containers
echo "Starting containers..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 10

# Run the setup script
echo "Running environment setup..."
docker-compose run --rm init

# Start the mock generator
echo "Starting mock generator..."
docker-compose up -d mock_generator

echo "Environment is ready!"
echo "Services:"
echo "- LocalStack: http://localhost:4566"
echo "- MinIO Console: http://localhost:9001"
echo "- Trino: http://localhost:8080"
echo "- Mock Generator: Running in background"

# Show logs
echo "Showing logs (press Ctrl+C to stop)..."
docker-compose logs -f 