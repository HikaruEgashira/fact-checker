import json
import os
import boto3
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

# Define the DynamoDB table name
TABLE_NAME = os.environ.get("TABLE_NAME") or "fact-check-results"

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
bedrock = boto3.client("bedrock-runtime")
processor = BatchProcessor(event_type=EventType.SQS)
logger = Logger()


def record_handler(record: SQSRecord):
    if TABLE_NAME is None:
        raise ValueError("TABLE_NAME environment variable is not set")
    text = record.body

    response = bedrock.converse(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": """
                            task: 次の文章をファクトチェックし結果のみ出力してください。
                            output format: "accurate" | "inaccurate" | "false" | "indeterminate"
                            example1: "Yesterday was Monday." → "indeterminate"
                            example2: "The text to be fact-checked." → "accurate"
                            example3: "The moon is made of cheese." → "false"
                            example4: "The earth is flat." → "inaccurate"
                            example5: "The earth is round." → "accurate"
                        """
                    }
                ],
            },
            {"role": "assistant", "content": [{"text": "accurate"}]},
            {
                "role": "user",
                "content": [{"text": text}],
            },
        ],
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )
    response_text = response["output"]["message"]["content"][0]["text"]  # type: ignore
    if response_text not in ["accurate", "inaccurate", "false", "indeterminate"]:
        raise ValueError(f"Invalid response: {response_text}")

    logger.info(f"Received response: {response_text}")
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(
        Item={"task_id": record.message_id, "result": response_text, "text": text}
    )


def lambda_handler(event, context: LambdaContext):
    return process_partial_response(
        event=event,
        record_handler=record_handler,
        processor=processor,
        context=context,
    )


if __name__ == "__main__":
    event = {
        "Records": [
            {
                "messageId": "test-message-id",
                "receiptHandle": "test-receipt-handle",
                "body": "The text to be fact-checked.",
                "attributes": {},
                "messageAttributes": {},
                "md5OfBody": "test-md5",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:region:account-id:queue-name",
                "awsRegion": "region",
            }
        ]
    }
    lambda_handler(event, LambdaContext())