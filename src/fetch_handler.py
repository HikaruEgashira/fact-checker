import os
import boto3
import json
from typing import Any, Dict
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize AWS clients
sts = boto3.client("sts")
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")

# Define the SQS queue URL and DynamoDB table name
TABLE_NAME = os.environ.get("TABLE_NAME") or "fact-check-results"
QUEUE_NAME = os.environ.get("QUEUE_NAME") or "fact-check-queue"
REGION = os.environ.get("AWS_REGION") or "ap-northeast-1"
QUEUE_URL = f"https://sqs.{REGION}.amazonaws.com/{sts.get_caller_identity()['Account']}/{QUEUE_NAME}"


def enqueue_fact_check_task(event, context: LambdaContext) -> Dict[str, Any]:
    body = json.loads(event["body"])
    text = body["text"]

    # Send the task to the queue
    response = sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=text)

    task_id = response["MessageId"]

    return {"statusCode": 200, "body": json.dumps({"task_id": task_id})}


def check_task_status(event, context: LambdaContext) -> Dict[str, Any]:
    if TABLE_NAME is None:
        return {"statusCode": 500, "body": json.dumps({"error": "Configuration error"})}
    task_id = event["pathParameters"]["task_id"]

    # Retrieve the task result from DynamoDB
    response = dynamodb.Table(TABLE_NAME).get_item(Key={"task_id": task_id})

    if "Item" in response:
        result = response["Item"]["result"]
        return {
            "statusCode": 200,
            "body": json.dumps({"task_id": task_id, "result": result}),
        }
    else:
        return {"statusCode": 404, "body": json.dumps({"error": "Task not found"})}


def lambda_handler(event, context: LambdaContext) -> Dict[str, Any]:
    if event["httpMethod"] == "POST" and event["path"] == "/fact-check":
        return enqueue_fact_check_task(event, context)
    elif (
        event["httpMethod"] == "GET"
        and event["path"].startswith("/fact-check/")
        and "task_id" in event["pathParameters"]
    ):
        return check_task_status(event, context)
    else:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid request"})}
