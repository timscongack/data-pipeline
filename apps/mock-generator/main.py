import json
import random
import datetime
import boto3
from typing import Dict, Any

def generate_mock_event() -> Dict[str, Any]:
    """Generate a mock API event with random data."""
    event_types = ["user_login", "product_view", "cart_update", "purchase"]
    user_ids = [f"user_{i}" for i in range(1, 1001)]
    
    return {
        "event_id": str(random.randint(100000, 999999)),
        "event_type": random.choice(event_types),
        "user_id": random.choice(user_ids),
        "timestamp": datetime.datetime.now().isoformat(),
        "metadata": {
            "browser": random.choice(["chrome", "firefox", "safari", "edge"]),
            "os": random.choice(["windows", "macos", "linux", "android", "ios"]),
            "device": random.choice(["desktop", "mobile", "tablet"])
        }
    }

def send_to_lambda(event: Dict[str, Any]) -> None:
    """Send the mock event to a Lambda function."""
    lambda_client = boto3.client(
        'lambda',
        endpoint_url='http://localhost:4566',
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    try:
        response = lambda_client.invoke(
            FunctionName='data-processor',
            InvocationType='Event',
            Payload=json.dumps(event)
        )
        print(f"Event sent successfully: {event['event_id']}")
    except Exception as e:
        print(f"Error sending event: {str(e)}")

if __name__ == "__main__":
    # Generate and send 10 mock events
    for _ in range(10):
        event = generate_mock_event()
        send_to_lambda(event) 