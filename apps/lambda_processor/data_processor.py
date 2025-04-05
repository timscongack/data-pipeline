import json
import io
import gzip
import uuid
import traceback
import polars as pl
from datetime import datetime
from typing import Dict, Any, Optional
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table

_catalog = None

def get_catalog():
    """Get or initialize the catalog."""
    global _catalog
    if _catalog is None:
        _catalog = load_catalog("glue", warehouse="s3://iceberg-data/warehouse")
    return _catalog

def log_error(
    error_type: str,
    error_message: str,
    event_id: Optional[str] = None,
    event_type: Optional[str] = None,
    event_data: Optional[Dict[str, Any]] = None,
    processing_stage: str = "unknown"
) -> None:
    """Log error to Iceberg error_logs table."""
    try:
        error_id = str(uuid.uuid4())
        error_data = {
            "error_id": error_id,
            "timestamp": datetime.utcnow(),
            "event_id": event_id,
            "event_type": event_type,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": traceback.format_exc(),
            "processing_stage": processing_stage,
            "event_data": json.dumps(event_data) if event_data else None
        }
        
        # Create DataFrame
        df = pl.DataFrame([error_data])
        
        # Write to error_logs table
        table = get_catalog().load_table("error_logs")
        table.append(df.to_arrow())
        
    except Exception as e:
        # If error logging fails, print to console as last resort
        print(f"Failed to log error: {str(e)}")
        print(f"Original error: {error_message}")

def flatten_nested_dict(d: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
    """Flatten a nested dictionary with optional prefix."""
    try:
        items = []
        for k, v in d.items():
            new_key = f"{prefix}{k}" if prefix else k
            if isinstance(v, dict):
                items.extend(flatten_nested_dict(v, f"{new_key}_").items())
            else:
                items.append((new_key, v))
        return dict(items)
    except Exception as e:
        log_error(
            "FlattenError",
            str(e),
            processing_stage="flatten_nested_dict"
        )
        raise

def process_event(event: Dict[str, Any]) -> pl.DataFrame:
    """Process a single event and return a DataFrame."""
    try:
        # Validate required fields
        required_fields = ["event_id", "event_type", "user_id", "timestamp"]
        for field in required_fields:
            if field not in event:
                raise ValueError(f"Missing required field: {field}")
        
        # Flatten the nested structure
        flattened = flatten_nested_dict(event)
        
        # Create DataFrame
        df = pl.DataFrame([flattened])
        
        # Ensure timestamp is in correct format
        df = df.with_columns(
            pl.col("timestamp").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.fZ")
        )
        
        # Rename columns to remove leading underscore from _doc
        for col in df.columns:
            if col.startswith("_doc_"):
                df = df.rename({col: col[1:]})
        
        return df
    except Exception as e:
        log_error(
            "ProcessingError",
            str(e),
            event_id=event.get("event_id"),
            event_type=event.get("event_type"),
            event_data=event,
            processing_stage="process_event"
        )
        raise

def write_to_iceberg(df: pl.DataFrame, event_type: str) -> None:
    """Write DataFrame to appropriate Iceberg table based on event type."""
    try:
        # Get the appropriate table
        table_name = f"events_{event_type}"
        table = get_catalog().load_table(table_name)
        
        # Convert to PyArrow table
        arrow_table = df.to_arrow()
        
        # Write to Iceberg
        table.append(arrow_table)
    except Exception as e:
        log_error(
            "WriteError",
            str(e),
            event_id=df["event_id"][0] if "event_id" in df.columns else None,
            event_type=event_type,
            processing_stage="write_to_iceberg"
        )
        raise

def compress_data(data: bytes) -> bytes:
    """Compress data using gzip."""
    try:
        if isinstance(data, bytes):
            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
                f.write(data)
            return buffer.getvalue()
        return data
    except Exception as e:
        log_error(
            "CompressionError",
            str(e),
            processing_stage="compress_data"
        )
        raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda function handler."""
    try:
        # Process the event
        df = process_event(event)
        
        # Write to appropriate table based on event type
        event_type = event["event_type"]
        write_to_iceberg(df, event_type)
        
        # Generate S3 key for the event
        s3_key = f"events/{event_type}/{datetime.utcnow().strftime('%Y/%m/%d')}/{event['event_id']}.parquet"
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "event_id": event["event_id"],
                "status": "success",
                "s3_key": s3_key,
                "timestamp": datetime.utcnow().isoformat()
            })
        }
    except Exception as e:
        log_error(
            "HandlerError",
            str(e),
            event_id=event.get("event_id"),
            event_type=event.get("event_type"),
            event_data=event,
            processing_stage="lambda_handler"
        )
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "event_id": event.get("event_id", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            })
        } 