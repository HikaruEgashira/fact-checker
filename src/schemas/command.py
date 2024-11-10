import os
from typing import Literal, Union
import boto3
from aws_lambda_powertools.utilities.parser import BaseModel, Field

from schemas.state import current_session

QUEUE_NAME = os.environ.get("QUEUE_NAME") or "fact-checker-queue"
REGION = os.environ.get("AWS_REGION") or "ap-northeast-1"

session = boto3.Session()
sqs = session.client("sqs")
sts = session.client("sts")

queue_url = f"https://sqs.{REGION}.amazonaws.com/{sts.get_caller_identity()['Account']}/{QUEUE_NAME}"

# Command pattern
# https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions


class EntryCommand(BaseModel):
    type: Literal["entry"] = "entry"
    prompt: str


class UnknownCommand(BaseModel):
    type: Literal["unknown"] = "unknown"


Command = Union[EntryCommand, UnknownCommand]


class Request(BaseModel):
    command: Command = Field(..., discriminator="type")
    id: str


# Utility functions


def send_command(command: Command):
    request = Request(id=current_session(), command=command)
    return sqs.send_message(QueueUrl=queue_url, MessageBody=request.model_dump_json())


def send_batch(commands: list[Command]):
    return sqs.send_message_batch(
        QueueUrl=queue_url,
        Entries=[
            {
                "Id": str(i),
                "MessageBody": Request(
                    id=current_session(), command=command
                ).model_dump_json(),
            }
            for i, command in enumerate(commands)
        ],
    )
