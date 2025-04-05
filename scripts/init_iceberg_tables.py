import boto3
import pyiceberg
from pyiceberg.catalog import GlueCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    StringType,
    LongType,
    IntegerType,
    BooleanType,
    DoubleType,
    TimestampType,
    StructType,
    NestedField
)

def create_base_schema():
    """Create base schema for event tables."""
    return Schema(
        NestedField(1, "event_id", StringType(), required=True),
        NestedField(2, "event_type", StringType(), required=True),
        NestedField(3, "user_id", StringType(), required=True),
        NestedField(4, "timestamp", TimestampType(), required=True),
        NestedField(5, "browser", StringType()),
        NestedField(6, "os", StringType()),
        NestedField(7, "device", StringType()),
        NestedField(8, "doc_session_info_session_id", StringType()),
        NestedField(9, "doc_session_info_duration", IntegerType()),
        NestedField(10, "doc_session_info_pages_visited", IntegerType()),
        NestedField(11, "doc_session_info_entry_page", StringType()),
        NestedField(12, "doc_session_info_exit_page", StringType()),
        NestedField(13, "doc_session_info_referrer", StringType()),
        NestedField(14, "doc_session_info_is_new_session", BooleanType()),
        NestedField(15, "doc_user_agent_browser_version", StringType()),
        NestedField(16, "doc_user_agent_platform_version", StringType()),
        NestedField(17, "doc_user_agent_device_type", StringType()),
        NestedField(18, "doc_user_agent_screen_resolution", StringType()),
        NestedField(19, "doc_user_agent_language", StringType()),
        NestedField(20, "doc_user_agent_timezone", StringType()),
        NestedField(21, "doc_location_country", StringType()),
        NestedField(22, "doc_location_region", StringType()),
        NestedField(23, "doc_location_city", StringType()),
        NestedField(24, "doc_location_ip_address", StringType()),
        NestedField(25, "doc_location_isp", StringType()),
        NestedField(26, "doc_location_connection_type", StringType()),
        NestedField(27, "doc_engagement_scroll_depth", IntegerType()),
        NestedField(28, "doc_engagement_time_on_page", IntegerType()),
        NestedField(29, "doc_engagement_interactions", IntegerType()),
        NestedField(30, "doc_engagement_form_submissions", IntegerType()),
        NestedField(31, "doc_engagement_video_views", IntegerType()),
        NestedField(32, "doc_engagement_downloads", IntegerType()),
        NestedField(33, "doc_performance_page_load_time", DoubleType()),
        NestedField(34, "doc_performance_dom_load_time", DoubleType()),
        NestedField(35, "doc_performance_network_latency", DoubleType()),
        NestedField(36, "doc_performance_server_response_time", DoubleType())
    )

def create_error_log_schema():
    """Create schema for error logging table."""
    return Schema(
        NestedField(1, "error_id", StringType(), required=True),
        NestedField(2, "timestamp", TimestampType(), required=True),
        NestedField(3, "event_id", StringType()),
        NestedField(4, "event_type", StringType()),
        NestedField(5, "error_type", StringType(), required=True),
        NestedField(6, "error_message", StringType(), required=True),
        NestedField(7, "stack_trace", StringType()),
        NestedField(8, "processing_stage", StringType(), required=True),
        NestedField(9, "event_data", StringType())
    )

def create_table(catalog, table_name, schema, partition_spec=None):
    """Create an Iceberg table with standard properties."""
    properties = {
        "write.format.default": "parquet",
        "write.parquet.compression-codec": "zstd",
        "write.parquet.row-group-size-bytes": "134217728",
        "write.parquet.page-size-bytes": "1048576",
        "write.metadata.compression-codec": "gzip",
        "write.metadata.metrics.default": "truncate(16)"
    }
    
    if partition_spec is None:
        partition_spec = ["timestamp"]
    
    catalog.create_table(
        table_name,
        schema,
        partition_spec=partition_spec,
        properties=properties
    )

def create_tables():
    """Create all required Iceberg tables."""
    # Create catalog
    catalog = GlueCatalog("events_db")
    
    # Create base schema
    base_schema = create_base_schema()
    
    # Create error logging table
    error_schema = create_error_log_schema()
    create_table(catalog, "error_logs", error_schema, ["timestamp"])
    
    # Create event type-specific tables
    event_types = [
        "user_login",
        "product_view",
        "cart_update",
        "purchase",
        "page_view",
        "search",
        "click",
        "form_submission"
    ]
    
    for event_type in event_types:
        table_name = f"events_{event_type}"
        create_table(catalog, table_name, base_schema)

if __name__ == "__main__":
    create_tables() 