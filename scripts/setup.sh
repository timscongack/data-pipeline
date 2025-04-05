#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Data Pipeline Setup..."

# Start Localstack
echo "📦 Starting Localstack..."
docker-compose -f docker/localstack/docker-compose.yml up -d

# Wait for Localstack to be ready
echo "⏳ Waiting for Localstack to be ready..."
until curl -s http://localhost:4566/_localstack/health | grep -q '"s3": "running"'; do
  sleep 2
done

# Check if infrastructure exists
echo "🔍 Checking if infrastructure exists..."
if ! aws --endpoint-url=http://localhost:4566 s3 ls s3://iceberg-data-dev 2>/dev/null; then
    echo "🏗️  Infrastructure not found. Creating resources..."
    cd infrastructure/environments/dev
    terragrunt init
    terragrunt apply -auto-approve

    echo "🏗️  Creating storage resources..."
    cd storage
    terragrunt init
    terragrunt apply -auto-approve
    cd ../../../..
else
    echo "✅ Infrastructure already exists. Skipping Terraform."
fi

# Run tests
echo "🧪 Running tests..."
python -m pytest tests -v

# Start mock generator
echo "🤖 Starting mock generator..."
docker-compose up -d mock_generator

echo "✅ Setup complete! Services are running."
echo "📊 Access services at:"
echo "   - LocalStack: http://localhost:4566"
echo "   - MinIO Console: http://localhost:9001"
echo "   - Trino: http://localhost:8080" 