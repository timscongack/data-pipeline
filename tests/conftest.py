import pytest
import json
import random
import datetime
from typing import Dict, Any
import boto3
from moto import mock_aws
import os

@pytest.fixture
def sample_event() -> Dict[str, Any]:
    """Generate a sample event for testing.
    
    Returns:
        Dict[str, Any]: A sample event dictionary.
    """
    return {
        "event_id": "123456",
        "event_type": "user_login",
        "user_id": "user_1",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "metadata": {
            "browser": "chrome",
            "os": "windows",
            "device": "desktop"
        },
        "_doc": {
            "session_info": {
                "session_id": "session_1234",
                "duration": 3600,
                "pages_visited": 10,
                "entry_page": "/home",
                "exit_page": "/checkout",
                "referrer": "google",
                "is_new_session": True
            },
            "user_agent": {
                "browser_version": "100.0.0",
                "platform_version": "20.0.0",
                "device_type": "desktop",
                "screen_resolution": "1920x1080",
                "language": "en-US",
                "timezone": "UTC"
            },
            "location": {
                "country": "US",
                "region": "NA",
                "city": "New York",
                "ip_address": "192.168.1.1",
                "isp": "Comcast",
                "connection_type": "broadband"
            },
            "engagement": {
                "scroll_depth": 75,
                "time_on_page": 300,
                "interactions": 25,
                "form_submissions": 1,
                "video_views": 2,
                "downloads": 0
            },
            "performance": {
                "page_load_time": 1.5,
                "first_contentful_paint": 0.8,
                "dom_interactive": 1.2,
                "network_latency": 100
            }
        }
    }

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def s3(aws_credentials):
    """Mocked S3 client."""
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='data-pipeline-bucket')
        yield s3

@pytest.fixture
def lambda_client(aws_credentials):
    """Mocked Lambda client."""
    with mock_aws():
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        yield lambda_client

@pytest.fixture
def mock_context():
    """Mock Lambda context."""
    class MockContext:
        def __init__(self):
            self.function_name = "test-function"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
            self.aws_request_id = "test-request-id"
    
    return MockContext() 