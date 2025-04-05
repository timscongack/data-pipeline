import time
import boto3
import os
from botocore.config import Config
from botocore.exceptions import ClientError

def wait_for_service(url, max_attempts=30, delay=2):
    """Wait for a service to become available."""
    import requests
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            if response.status_code < 500:
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"Waiting for service at {url}... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(delay)
    raise TimeoutError(f"Service at {url} did not become available")

def setup_aws_services():
    """Set up AWS services in Localstack."""
    # Configure boto3 for Localstack
    config = Config(
        region_name="us-east-1",
        retries={"max_attempts": 3}
    )
    
    # Initialize clients
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        config=config
    )
    
    glue = boto3.client(
        'glue',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        config=config
    )
    
    # Create S3 bucket
    try:
        s3.create_bucket(Bucket='iceberg-data')
        print("Created S3 bucket: iceberg-data")
    except ClientError as e:
        if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
            raise
    
    # Create Glue database
    try:
        glue.create_database(
            DatabaseInput={
                'Name': 'events_db',
                'Description': 'Database for event data'
            }
        )
        print("Created Glue database: events_db")
    except ClientError as e:
        if e.response['Error']['Code'] != 'AlreadyExistsException':
            raise

def setup_minio():
    """Set up MinIO bucket."""
    from minio import Minio
    
    # Initialize MinIO client
    client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    
    # Create bucket if it doesn't exist
    if not client.bucket_exists("iceberg-data"):
        client.make_bucket("iceberg-data")
        print("Created MinIO bucket: iceberg-data")

def setup_iceberg_tables():
    """Initialize Iceberg tables."""
    from scripts.init_iceberg_tables import create_tables
    create_tables()
    print("Created Iceberg tables")

def main():
    """Main setup function."""
    print("Starting environment setup...")
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    wait_for_service("http://localhost:4566")
    wait_for_service("http://localhost:9000")
    wait_for_service("http://localhost:8080")
    
    # Set up services
    print("Setting up AWS services...")
    setup_aws_services()
    
    print("Setting up MinIO...")
    setup_minio()
    
    print("Setting up Iceberg tables...")
    setup_iceberg_tables()
    
    print("Environment setup complete!")

if __name__ == "__main__":
    main() 