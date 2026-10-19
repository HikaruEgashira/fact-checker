import json

from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

from lambda_worker import record_handler
from schemas.state import State, update_state


def test_worker():
    state_id = "test-state-id"

    event = SQSRecord(
        {
            "messageId": "test-message-id",
            "receiptHandle": "test-receipt-handle",
            "body": json.dumps(
                {
                    "id": state_id,
                    "command": {
                        "type": "factcheck",
                        "prompt": "The earth is round.",
                    },
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
    # setup
    dummy_state = State(
        id=state_id,
        status="pending",
        output="",
    )
    update_state(dummy_state)

    record_handler(event)
