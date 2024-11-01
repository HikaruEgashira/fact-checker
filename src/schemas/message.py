import os
from typing import Literal
from aws_lambda_powertools.utilities.parser import BaseModel
from schemas.aws import session

QUEUE_NAME = os.environ.get("QUEUE_NAME") or "fact-checker-queue"
REGION = os.environ.get("AWS_REGION") or "ap-northeast-1"

sqs = session.client("sqs")
sts = session.client("sts")

queue_url = f"https://sqs.{REGION}.amazonaws.com/{sts.get_caller_identity()['Account']}/{QUEUE_NAME}"


ActionType = Literal["execute"]


class ExecuteMessage(BaseModel):
    type: ActionType = "execute"
    text: str
    task_id: str


def send_message(message: BaseModel):
    message_raw = message.model_dump_json()
    return sqs.send_message(QueueUrl=queue_url, MessageBody=message_raw)
