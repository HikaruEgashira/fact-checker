from lambda_worker import record_handler
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
import pytest
import json


def test_record_handler():
    event = SQSRecord(
        {
            "messageId": "test-message-id",
            "receiptHandle": "test-receipt-handle",
            "body": json.dumps(
                {
                    "type": "execute",
                    "text": "The text to be fact-checked.",
                    "task_id": "test-task-id",
                }
            ),
            "attributes": {},
            "messageAttributes": {},
            "md5OfBody": "test-md5",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:region:account-id:queue-name",
            "awsRegion": "region",
        }
    )
    try:
        record_handler(event)
    except Exception as e:
        pytest.fail(f"record_handler raised an exception: {e}")
