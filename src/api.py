import os
import json
import uuid
from typing import Any, Dict
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)

from schemas.task import Task, session, update_task
from schemas.message import send_message
from src.schemas.message import ExecuteMessage


# Define the SQS queue URL and DynamoDB table name
TABLE_NAME = os.environ.get("TABLE_NAME") or "fact-check-results"

# Initialize AWS clients
sts = session.client("sts")
sqs = session.client("sqs")
dynamodb = session.resource("dynamodb")


def enqueue_fact_check_task(event, context: LambdaContext):
    body = json.loads(event["body"])
    text = body["text"]

    # Save the task to DynamoDB
    task_id = context.aws_request_id if context else str(uuid.uuid4())
    task = Task(task_id=task_id, text=text, result="pending")
    update_task(task)

    # Send the task to the queue
    message = ExecuteMessage(text=text, task_id=task_id)
    response = send_message(message)

    return {
        "statusCode": 200,
        "body": json.dumps({"task_id": task_id, "sqs_id": response["MessageId"]}),
    }


def check_task_status(event, context: LambdaContext):
    task_id = event["pathParameters"]["task_id"]

    # Retrieve the task result from DynamoDB
    response = dynamodb.Table(TABLE_NAME).get_item(Key={"task_id": task_id})

    if "Item" in response:
        result = response["Item"]["result"]
        body = {"task_id": task_id, "result": result}
        return {"statusCode": 200, "body": json.dumps(body)}
    else:
        body = {"error": "Task not found"}
        return {"statusCode": 404, "body": json.dumps(body)}


@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    if event.http_method == "POST" and event.path == "/fact-check":
        return enqueue_fact_check_task(event, context)
    elif (
        event.http_method == "GET"
        and event.path.startswith("/fact-check/")
        and "task_id" in event.path_parameters
    ):
        return check_task_status(event, context)
    else:
        body = {"error": "Invalid request"}
        return {"statusCode": 400, "body": json.dumps(body)}
