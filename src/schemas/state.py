import os
from typing import Literal
import boto3
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.logging import Logger


TABLE_NAME = os.environ.get("TABLE_NAME") or "fact-checker-results"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
logger = Logger()

FactCheckOutput = str
Status = Literal["pending", "running", "completed"]

_session_id: str


def current_session():
    if not _session_id:
        logger.error("call current_session() before setting the session_id")
    return _session_id


class State(BaseModel):
    id: str
    status: Status
    output: FactCheckOutput


def update_state(state: State):
    global _session_id
    _session_id = state.id
    item = state.model_dump()
    return table.put_item(Item=item)


def get_state(state_id: str):
    global _session_id
    _session_id = state_id
    response = table.get_item(Key={"id": state_id})
    return State(**response["Item"]) if "Item" in response else None  # type: ignore


# only for testing purposes
def delete_state(state_id: str):
    return table.delete_item(Key={"id": state_id})
