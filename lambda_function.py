import json
import os
import uuid
from datetime import datetime
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("DDB_TABLE", "DG_Events")
table = dynamodb.Table(TABLE_NAME)

def extract_username(detail):
    # event may include userIdentity with userName, or principal
    ui = detail.get("userIdentity", {})
    return ui.get("userName") or ui.get("principalId") or "Unknown"

def lambda_handler(event, context):
    # EventBridge events: top-level 'detail' with specifics
    # We'll extract required fields: Event time, source, event name, resource name, region, username
    try:
        event_time = event.get("time") or datetime.utcnow().isoformat()
        source = event.get("source", "unknown")
        detail = event.get("detail", {})
        event_name = detail.get("eventName") or detail.get("name") or "UnknownEvent"

        # Resource name detection for S3 and EC2
        resource_name = "UnknownResource"
        if source == "aws.s3":
            # S3 CreateBucket/DeleteBucket events contain bucket name in detail.bucketName or resources
            resource_name = detail.get("requestParameters", {}).get("bucketName") \
                            or detail.get("bucketName") \
                            or next((r.get("ARN","").split(":")[-1] for r in event.get("resources",[]) if "bucket" in r.get("ARN","")), "UnknownBucket")
        elif source == "aws.ec2":
            # For EC2 start/stop, instance-id is normally in detail.instance-id or resources
            resource_name = detail.get("instance-id") or detail.get("instanceId") or next((r.get("ARN","").split("/")[-1] for r in event.get("resources",[]) if "instance" in r.get("ARN","")), "UnknownInstance")

        region = event.get("region") or detail.get("awsRegion") or os.environ.get("AWS_REGION", "unknown")
        username = extract_username(detail)

        item = {
            "EventId": str(uuid.uuid4()),
            "EventTime": event_time,
            "EventSource": source,
            "EventName": event_name,
            "ResourceName": resource_name,
            "Region": region,
            "Username": username
        }

        table.put_item(Item=item)
        print("Saved event:", item)
        return {"statusCode": 200, "body": json.dumps({"message":"ok", "item": item})}
    except Exception as exc:
        print("Error:", exc)
        return {"statusCode": 500, "body": json.dumps({"error": str(exc)})}
