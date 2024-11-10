from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

from schemas.command import Request
from actions.entry import entry_action
from schemas.state import get_state

# Initialize AWS clients
processor = BatchProcessor(event_type=EventType.SQS)
logger = Logger()


def record_handler(record: SQSRecord):
    logger.info(f"Processing record: {record.json_body}")
    req = Request(**record.json_body)
    state = get_state(req.id)
    if state is None or state.status != "pending":
        logger.warning(f"Invalid state: {req.id}")
        return

    match req.command.type:
        case "entry":
            entry_action(req.command)
        case _:
            raise ValueError(f"Invalid command type: {req.command.type}")


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
