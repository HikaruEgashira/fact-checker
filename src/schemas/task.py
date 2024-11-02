import os
from typing import Literal, Union
import boto3
from aws_lambda_powertools.utilities.parser import BaseModel


TABLE_NAME = os.environ.get("TABLE_NAME") or "fact-checker-results"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

FactCheckOutput = Literal["accurate", "inaccurate", "false", "indeterminate"]
Status = Union[Literal["pending"], FactCheckOutput]


class Task(BaseModel):
    task_id: str
    text: str
    result: Status


def update_task(task: Task):
    return table.put_item(Item=task.model_dump())


def get_task(task_id: str):
    response = table.get_item(Key={"task_id": task_id})
    return Task(**response["Item"]) if "Item" in response else None  # type: ignore


# only for testing purposes
def delete_task(task_id: str):
    return table.delete_item(Key={"task_id": task_id})
