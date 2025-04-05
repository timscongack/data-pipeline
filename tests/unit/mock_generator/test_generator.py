import pytest
from apps.mock_generator.main import (
    generate_session_info,
    generate_user_agent,
    generate_location,
    generate_engagement,
    generate_mock_event,
    send_to_lambda
)

def test_generate_session_info():
    """Test session info generation."""
    session_info = generate_session_info()
    
    assert isinstance(session_info, dict)
    assert "session_id" in session_info
    assert "duration" in session_info
    assert "pages_visited" in session_info
    assert "entry_page" in session_info
    assert "exit_page" in session_info
    assert "referrer" in session_info
    assert "is_new_session" in session_info
    
    assert isinstance(session_info["duration"], int)
    assert 1 <= session_info["duration"] <= 3600
    assert isinstance(session_info["pages_visited"], int)
    assert 1 <= session_info["pages_visited"] <= 20
    assert isinstance(session_info["is_new_session"], bool)

def test_generate_user_agent():
    """Test user agent generation."""
    user_agent = generate_user_agent()
    
    assert isinstance(user_agent, dict)
    assert "browser_version" in user_agent
    assert "platform_version" in user_agent
    assert "device_type" in user_agent
    assert "screen_resolution" in user_agent
    assert "language" in user_agent
    assert "timezone" in user_agent
    
    assert isinstance(user_agent["device_type"], str)
    assert user_agent["device_type"] in ["desktop", "mobile", "tablet"]
    assert isinstance(user_agent["language"], str)
    assert user_agent["language"] in ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"]

def test_generate_location():
    """Test location generation."""
    location = generate_location()
    
    assert isinstance(location, dict)
    assert "country" in location
    assert "region" in location
    assert "city" in location
    assert "ip_address" in location
    assert "isp" in location
    assert "connection_type" in location
    
    assert isinstance(location["country"], str)
    assert location["country"] in ["US", "UK", "CA", "AU", "DE"]
    assert isinstance(location["connection_type"], str)
    assert location["connection_type"] in ["broadband", "mobile", "dial-up"]

def test_generate_engagement():
    """Test engagement metrics generation."""
    engagement = generate_engagement()
    
    assert isinstance(engagement, dict)
    assert "scroll_depth" in engagement
    assert "time_on_page" in engagement
    assert "interactions" in engagement
    assert "form_submissions" in engagement
    assert "video_views" in engagement
    assert "downloads" in engagement
    
    assert isinstance(engagement["scroll_depth"], int)
    assert 0 <= engagement["scroll_depth"] <= 100
    assert isinstance(engagement["time_on_page"], int)
    assert 1 <= engagement["time_on_page"] <= 600

def test_generate_mock_event():
    """Test mock event generation."""
    event = generate_mock_event()
    
    assert isinstance(event, dict)
    assert "event_id" in event
    assert "event_type" in event
    assert "user_id" in event
    assert "timestamp" in event
    assert "metadata" in event
    assert "_doc" in event
    
    assert isinstance(event["event_type"], str)
    assert event["event_type"] in ["user_login", "product_view", "cart_update", "purchase"]
    assert isinstance(event["metadata"], dict)
    assert "browser" in event["metadata"]
    assert "os" in event["metadata"]
    assert "device" in event["metadata"]
    
    assert isinstance(event["_doc"], dict)
    assert "session_info" in event["_doc"]
    assert "user_agent" in event["_doc"]
    assert "location" in event["_doc"]
    assert "engagement" in event["_doc"]
    assert "performance" in event["_doc"]

@pytest.mark.benchmark
def test_generate_mock_event_performance(benchmark):
    """Benchmark mock event generation performance."""
    result = benchmark(generate_mock_event)
    assert isinstance(result, dict)

def test_send_to_lambda(mocker, sample_event):
    """Test Lambda invocation."""
    # Mock boto3 client
    mock_lambda = mocker.patch('boto3.client')
    mock_invoke = mock_lambda.return_value.invoke
    
    # Call the function
    send_to_lambda(sample_event)
    
    # Verify Lambda was called correctly
    mock_invoke.assert_called_once_with(
        FunctionName='data-processor',
        InvocationType='Event',
        Payload=mocker.ANY  # We don't care about the exact payload
    ) 