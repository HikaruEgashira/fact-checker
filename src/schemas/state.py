import os
from typing import Literal, Union
import boto3
from aws_lambda_powertools.utilities.parser import BaseModel


TABLE_NAME = os.environ.get("TABLE_NAME") or "fact-checker-results"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

FactCheckOutput = Literal["accurate", "inaccurate", "false", "indeterminate"]
Status = Union[Literal["pending"], FactCheckOutput]


class State(BaseModel):
    id: str
    result: Status


def update_state(state: State):
    return table.put_item(Item=state.model_dump())


def get_state(state_id: str):
    response = table.get_item(Key={"id": state_id})
    return State(**response["Item"]) if "Item" in response else None  # type: ignore


# only for testing purposes
def delete_state(state_id: str):
    return table.delete_item(Key={"id": state_id})
