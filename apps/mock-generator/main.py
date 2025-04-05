import json
import random
import datetime
import boto3
from typing import Dict, Any, List

def generate_session_info() -> Dict[str, Any]:
    """Generate session-related information.
    
    Returns:
        Dict[str, Any]: Dictionary containing session information including ID, duration, pages visited,
        entry/exit pages, referrer, and session status.
    """
    return {
        "session_id": f"session_{random.randint(1000, 9999)}",
        "duration": random.randint(1, 3600),  #duration in seconds
        "pages_visited": random.randint(1, 20),
        "entry_page": random.choice(["/home", "/products", "/blog", "/about"]),
        "exit_page": random.choice(["/checkout", "/product", "/contact", "/home"]),
        "referrer": random.choice(["google", "direct", "social", "email", "other"]),
        "is_new_session": random.choice([True, False])
    }

def generate_user_agent() -> Dict[str, Any]:
    """Generate user agent and device information.
    
    Returns:
        Dict[str, Any]: Dictionary containing browser version, platform version, device type,
        screen resolution, language, and timezone information.
    """
    return {
        "browser_version": f"{random.randint(1, 100)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        "platform_version": f"{random.randint(10, 20)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        "device_type": random.choice(["desktop", "mobile", "tablet"]),
        "screen_resolution": random.choice(["1920x1080", "1366x768", "1440x900", "375x812"]),
        "language": random.choice(["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"]),
        "timezone": random.choice(["UTC", "EST", "PST", "CET", "GMT"])
    }

def generate_location() -> Dict[str, Any]:
    """Generate location and network information.
    
    Returns:
        Dict[str, Any]: Dictionary containing country, region, city, IP address,
        ISP, and connection type information.
    """
    return {
        "country": random.choice(["US", "UK", "CA", "AU", "DE"]),
        "region": random.choice(["NA", "EU", "AP", "SA"]),
        "city": random.choice(["New York", "London", "Toronto", "Sydney", "Berlin"]),
        "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
        "isp": random.choice(["Comcast", "Verizon", "AT&T", "BT", "Deutsche Telekom"]),
        "connection_type": random.choice(["broadband", "mobile", "dial-up"])
    }

def generate_engagement() -> Dict[str, Any]:
    """Generate user engagement metrics.
    
    Returns:
        Dict[str, Any]: Dictionary containing scroll depth, time on page, interactions,
        form submissions, video views, and downloads information.
    """
    return {
        "scroll_depth": random.randint(0, 100),  #percentage
        "time_on_page": random.randint(1, 600),  #seconds
        "interactions": random.randint(0, 50),
        "form_submissions": random.randint(0, 3),
        "video_views": random.randint(0, 5),
        "downloads": random.randint(0, 2)
    }

def generate_mock_event() -> Dict[str, Any]:
    """Generate a mock API event with comprehensive nested _doc field.
    
    Returns:
        Dict[str, Any]: Dictionary containing event ID, type, user ID, timestamp,
        metadata, and nested _doc information.
    """
    event_types = ["user_login", "product_view", "cart_update", "purchase"]
    user_ids = [f"user_{i}" for i in range(1, 1001)]
    
    #generate nested _doc data
    _doc = {
        "session_info": generate_session_info(),
        "user_agent": generate_user_agent(),
        "location": generate_location(),
        "engagement": generate_engagement(),
        "performance": {
            "page_load_time": random.uniform(0.5, 5.0),
            "first_contentful_paint": random.uniform(0.3, 3.0),
            "dom_interactive": random.uniform(0.4, 4.0),
            "network_latency": random.uniform(10, 500)
        }
    }
    
    return {
        "event_id": str(random.randint(100000, 999999)),
        "event_type": random.choice(event_types),
        "user_id": random.choice(user_ids),
        "timestamp": datetime.datetime.now().isoformat(),
        "metadata": {
            "browser": random.choice(["chrome", "firefox", "safari", "edge"]),
            "os": random.choice(["windows", "macos", "linux", "android", "ios"]),
            "device": random.choice(["desktop", "mobile", "tablet"])
        },
        "_doc": _doc
    }

def send_to_lambda(event: Dict[str, Any]) -> None:
    """Send the mock event to a Lambda function.
    
    Args:
        event (Dict[str, Any]): The event data to send to the Lambda function.
    """
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
        print(f"event sent successfully: {event['event_id']}")
    except Exception as e:
        print(f"error sending event: {str(e)}")

if __name__ == "__main__":
    #generate and send 10 mock events
    for _ in range(10):
        event = generate_mock_event()
        send_to_lambda(event) 