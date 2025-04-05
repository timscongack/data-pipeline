import pytest
import polars as pl
import time
import io
import concurrent.futures
import psutil
import os
from unittest.mock import patch, MagicMock
from apps.lambda_processor.data_processor import (
    flatten_nested_dict,
    process_event,
    write_to_iceberg,
    lambda_handler,
    compress_data,
    get_catalog
)

@pytest.fixture(autouse=True)
def mock_catalog():
    """Mock Iceberg catalog for all tests."""
    with patch('apps.lambda_processor.data_processor.get_catalog') as mock_get_catalog:
        mock_catalog = MagicMock()
        mock_table = MagicMock()
        mock_catalog.load_table.return_value = mock_table
        mock_get_catalog.return_value = mock_catalog
        yield mock_catalog

def test_flatten_nested_dict():
    """Test flattening of nested dictionaries."""
    nested_dict = {
        "a": 1,
        "b": {
            "c": 2,
            "d": {
                "e": 3
            }
        }
    }
    
    expected = {
        "a": 1,
        "b_c": 2,
        "b_d_e": 3
    }
    
    result = flatten_nested_dict(nested_dict)
    assert result == expected

def test_flatten_nested_dict_with_prefix():
    """Test flattening with prefix."""
    nested_dict = {
        "a": 1,
        "b": {
            "c": 2
        }
    }
    
    expected = {
        "test_a": 1,
        "test_b_c": 2
    }
    
    result = flatten_nested_dict(nested_dict, "test_")
    assert result == expected

def test_process_event(sample_event):
    """Test event processing."""
    df = process_event(sample_event)
    
    assert isinstance(df, pl.DataFrame)
    assert len(df) == 1
    assert "event_id" in df.columns
    assert "doc_session_info_session_id" in df.columns
    assert "doc_user_agent_browser_version" in df.columns
    assert "doc_location_country" in df.columns
    assert "doc_engagement_scroll_depth" in df.columns
    assert "doc_performance_page_load_time" in df.columns

def test_compress_data():
    """Test data compression."""
    data = b"test data" * 100
    compressed = compress_data(data)
    
    assert isinstance(compressed, bytes)
    assert len(compressed) < len(data)

@pytest.mark.benchmark
def test_process_event_performance(benchmark, sample_event):
    """Benchmark event processing performance."""
    result = benchmark(process_event, sample_event)
    assert isinstance(result, pl.DataFrame)

@pytest.mark.benchmark
def test_compress_data_performance(benchmark):
    """Benchmark compression performance."""
    data = b"test data" * 1000
    result = benchmark(compress_data, data)
    assert isinstance(result, bytes)

def test_lambda_handler_success(sample_event, mock_context, s3):
    """Test successful Lambda execution."""
    response = lambda_handler(sample_event, mock_context)
    
    assert response["statusCode"] == 200
    assert "event_id" in response["body"]
    assert "s3_key" in response["body"]

def test_lambda_handler_error(sample_event, mock_context):
    """Test Lambda error handling."""
    # Remove required field to trigger error
    del sample_event["event_id"]
    
    response = lambda_handler(sample_event, mock_context)
    
    assert response["statusCode"] == 500
    assert "error" in response["body"]

def test_write_to_iceberg(mock_catalog, sample_event):
    """Test Iceberg write functionality."""
    df = process_event(sample_event)
    event_type = sample_event["event_type"]
    
    write_to_iceberg(df, event_type)
    
    # Verify write was called
    mock_catalog.load_table.assert_called_once_with(f"events_{event_type}")
    mock_table = mock_catalog.load_table.return_value
    mock_table.append.assert_called_once()

def test_data_integrity(sample_event):
    """Test data integrity through processing pipeline."""
    # Process event
    df = process_event(sample_event)
    
    # Verify all original data is preserved
    assert df["event_id"][0] == sample_event["event_id"]
    assert df["event_type"][0] == sample_event["event_type"]
    assert df["user_id"][0] == sample_event["user_id"]
    assert df["doc_session_info_session_id"][0] == sample_event["_doc"]["session_info"]["session_id"]
    assert df["doc_user_agent_browser_version"][0] == sample_event["_doc"]["user_agent"]["browser_version"]
    assert df["doc_location_country"][0] == sample_event["_doc"]["location"]["country"]
    assert df["doc_engagement_scroll_depth"][0] == sample_event["_doc"]["engagement"]["scroll_depth"]
    assert df["doc_performance_page_load_time"][0] == sample_event["_doc"]["performance"]["page_load_time"]

@pytest.mark.benchmark
def test_high_throughput_event_processing(benchmark, sample_event):
    """Test Lambda's ability to process multiple events per second."""
    # Process 1000 events and measure time
    def process_batch():
        for _ in range(1000):
            process_event(sample_event)
    
    # Benchmark the batch processing
    result = benchmark(process_batch)
    
    # Calculate events per second
    events_per_second = 1000 / benchmark.stats.stats.mean
    
    # Assert we can process at least 100 events per second
    assert events_per_second >= 100, f"Processing rate {events_per_second:.2f} events/sec is below required threshold"

@pytest.mark.benchmark
def test_concurrent_event_processing(benchmark, sample_event):
    """Test Lambda's ability to handle concurrent event processing."""
    def process_events_concurrently(num_events=100):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_event, sample_event) for _ in range(num_events)]
            concurrent.futures.wait(futures)
            return [f.result() for f in futures]
    
    # Benchmark concurrent processing
    result = benchmark(process_events_concurrently)
    
    # Calculate throughput
    events_per_second = 100 / benchmark.stats.stats.mean
    
    # Assert we can process at least 50 events per second concurrently
    assert events_per_second >= 50, f"Concurrent processing rate {events_per_second:.2f} events/sec is below required threshold"

@pytest.mark.benchmark
def test_memory_efficiency(benchmark, sample_event):
    """Test memory efficiency when processing multiple events."""
    def process_with_memory_check():
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process 100 events
        for _ in range(100):
            process_event(sample_event)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # Convert to MB
        
        return memory_increase
    
    # Benchmark memory usage
    memory_increase = benchmark(process_with_memory_check)
    
    # Assert memory increase is reasonable (less than 50MB for 100 events)
    assert memory_increase < 50, f"Memory increase {memory_increase:.2f}MB is too high for 100 events"

@pytest.mark.benchmark
def test_compression_performance(benchmark, sample_event):
    """Test compression performance."""
    def compress_batch():
        # Process 100 events
        df = pl.concat([process_event(sample_event) for _ in range(100)])
        
        # Write to bytes buffer
        buffer = io.BytesIO()
        df.write_parquet(buffer)
        data = buffer.getvalue()
        
        # Compress the data
        compressed = compress_data(data)
        
        # Calculate compression ratio
        compression_ratio = len(data) / len(compressed)
        assert compression_ratio >= 2.0, f"Compression ratio {compression_ratio:.2f} is below required threshold"
        
        return compressed
    
    # Benchmark compression
    result = benchmark(compress_batch)
    assert isinstance(result, bytes) 