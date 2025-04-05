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
    
    # Try up to 5 times with 2-second intervals
    for i in {1..5}; do
        if curl -s http://localhost:4566/_localstack/health | grep -q "\"s3\": \"available\""; then
            echo "Localstack is running and S3 is available"
            
            # Check if the S3 bucket exists
            if aws --endpoint-url=http://localhost:4566 s3 ls | grep -q "data-pipeline-dev"; then
                echo "S3 bucket 'data-pipeline-dev' exists"
                return 0
            else
                echo "S3 bucket 'data-pipeline-dev' not found"
                echo "Please create the infrastructure with:"
                echo "cd infrastructure/environments/dev"
                echo "terragrunt init"
                echo "terragrunt apply -auto-approve"
                exit 1
            fi
        fi
        echo "Attempt $i: Waiting for Localstack to be ready..."
        sleep 2
    done
    
    echo "Error: Localstack is not running or S3 is not available"
    echo "Please start Localstack with: docker-compose -f docker/localstack/docker-compose.yml up -d"
    echo "Then wait a few seconds and try again"
    exit 1
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

if ! command_exists aws; then
    echo "Error: AWS CLI is not installed"
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