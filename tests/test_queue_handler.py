from src.queue_handler import record_handler
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
import pytest


def test_record_handler() -> None:
    event = SQSRecord(
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
    )
    try:
        record_handler(event)
    except Exception as e:
        pytest.fail(f"record_handler raised an exception: {e}")
