FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for testing
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and tests
COPY . /app

# Set environment variables
ENV PYTHONPATH=/app
ENV AWS_ACCESS_KEY_ID=test
ENV AWS_SECRET_ACCESS_KEY=test
ENV AWS_DEFAULT_REGION=us-east-1
ENV AWS_ENDPOINT_URL=http://localstack:4566

# Create test script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Running tests..."\n\
python -m pytest tests/unit -v\n\
if [ $? -ne 0 ]; then\n\
    echo "Tests failed. Exiting."\n\
    exit 1\n\
fi\n\
echo "All tests passed. Starting mock generator..."\n\
exec python apps/mock_generator/main.py' > /app/entrypoint.sh && \
chmod +x /app/entrypoint.sh

# Use the test script as entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 