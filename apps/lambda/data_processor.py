import json
import boto3
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import io

s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

def process_event(event: Dict[str, Any]) -> pd.DataFrame:
    """Process a single event and return a DataFrame."""
    # Flatten the metadata
    flat_event = {
        'event_id': event['event_id'],
        'event_type': event['event_type'],
        'user_id': event['user_id'],
        'timestamp': event['timestamp'],
        'browser': event['metadata']['browser'],
        'os': event['metadata']['os'],
        'device': event['metadata']['device']
    }
    
    return pd.DataFrame([flat_event])

def write_to_s3(df: pd.DataFrame, bucket: str, key: str) -> None:
    """Write DataFrame to S3 as Parquet."""
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=parquet_buffer.getvalue()
    )

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda function handler."""
    try:
        # Process the event
        df = process_event(event)
        
        # Generate S3 key with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f'events/processed/{timestamp}_{event["event_id"]}.parquet'
        
        # Write to S3
        write_to_s3(df, 'data-pipeline-bucket', s3_key)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Event processed successfully',
                'event_id': event['event_id'],
                's3_key': s3_key
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing event',
                'error': str(e)
            })
        } 