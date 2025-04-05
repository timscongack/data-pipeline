FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/mock_generator /app/apps/mock_generator
COPY apps/lambda /app/apps/lambda

# Set environment variables
ENV PYTHONPATH=/app
ENV AWS_ACCESS_KEY_ID=test
ENV AWS_SECRET_ACCESS_KEY=test
ENV AWS_DEFAULT_REGION=us-east-1
ENV AWS_ENDPOINT_URL=http://localstack:4566

# Run the mock generator
CMD ["python", "apps/mock_generator/main.py"] 