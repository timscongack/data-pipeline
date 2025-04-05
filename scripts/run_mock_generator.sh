#!/bin/bash

# Exit on any error
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if services are ready
check_services() {
    echo "Checking if Localstack is running..."
    if ! curl -s http://localhost:4566/_localstack/health | grep -q "\"s3\": \"available\""; then
        echo "Error: Localstack is not running or S3 is not available"
        echo "Please start Localstack with: docker-compose -f docker/localstack/docker-compose.yml up -d"
        exit 1
    fi
    echo "Localstack is running and S3 is available"
}

# Function to run tests
run_tests() {
    echo "Running tests..."
    if ! python -m pytest tests/unit -v; then
        echo "Error: Tests failed"
        exit 1
    fi
    echo "Tests passed successfully"
}

# Function to create required directories
setup_directories() {
    echo "Setting up directories..."
    mkdir -p logs
}

# Check Python and required commands
if ! command_exists python; then
    echo "Error: Python is not installed"
    exit 1
fi

if ! command_exists pip; then
    echo "Error: pip is not installed"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Setup
setup_directories

# Check services
check_services

# Run tests
run_tests

# Start the mock generator
echo "Starting mock generator..."
python apps/mock_generator/main.py 2>&1 | tee logs/mock_generator.log 