import boto3
import json
import urllib3
import argparse
from typing import Any, Dict
from aws_lambda_powertools.utilities.typing import LambdaContext

# Initialize AWS clients
sqs = boto3.client("sqs")
dynamodb = boto3.client("dynamodb")

# Define the SQS queue URL and DynamoDB table name
QUEUE_URL = "https://sqs.<region>.amazonaws.com/<account-id>/<queue-name>"
TABLE_NAME = "<dynamodb-table-name>"


def handle_request(event, context: LambdaContext) -> Dict[str, Any]:
    body = json.loads(event["body"])
    text = body["text"]

    # Send the task to the queue
    response = sqs.send_message(
        QueueUrl=QUEUE_URL, MessageBody=json.dumps({"text": text})
    )

    task_id = response["MessageId"]

    return {"statusCode": 200, "body": json.dumps({"task_id": task_id})}


def check_task_status(event, context: LambdaContext) -> Dict[str, Any]:
    task_id = event["pathParameters"]["task_id"]

    # Retrieve the task result from DynamoDB
    response = dynamodb.get_item(TableName=TABLE_NAME, Key={"task_id": {"S": task_id}})

    if "Item" in response:
        result = response["Item"]["result"]["S"]
        return {
            "statusCode": 200,
            "body": json.dumps({"task_id": task_id, "result": result}),
        }
    else:
        return {"statusCode": 404, "body": json.dumps({"error": "Task not found"})}


def lambda_handler(event, context: LambdaContext) -> Dict[str, Any]:
    if event["httpMethod"] == "POST" and event["path"] == "/fact-check":
        return handle_request(event, context)
    elif event["httpMethod"] == "GET" and event["path"].startswith("/fact-check/"):
        return check_task_status(event, context)
    else:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid request"})}


def submit_fact_check_request(text: str) -> Dict[str, Any]:
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        "https://<api-endpoint>/fact-check",
        body=json.dumps({"text": text}),
        headers={"Content-Type": "application/json"},
    )
    return json.loads(response.data.decode("utf-8"))


def check_fact_check_status(task_id: str) -> Dict[str, Any]:
    http = urllib3.PoolManager()
    response = http.request(
        "GET",
        f"https://<api-endpoint>/fact-check/{task_id}",
        headers={"Content-Type": "application/json"},
    )
    return json.loads(response.data.decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Fact Checker CLI")
    subparsers = parser.add_subparsers(dest="command")

    submit_parser = subparsers.add_parser(
        "submit", help="Submit a fact-checking request"
    )
    submit_parser.add_argument(
        "--text", required=True, help="The text to be fact-checked"
    )

    status_parser = subparsers.add_parser(
        "status", help="Check the status of a fact-checking task"
    )
    status_parser.add_argument("--task_id", required=True, help="The task ID")

    args = parser.parse_args()

    if args.command == "submit":
        result = submit_fact_check_request(args.text)
        print(result)
    elif args.command == "status":
        result = check_fact_check_status(args.task_id)
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
