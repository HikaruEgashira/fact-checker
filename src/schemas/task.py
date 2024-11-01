import os
from typing import Literal, Union
from aws_lambda_powertools.utilities.parser import BaseModel
from aws import session

TABLE_NAME = os.environ.get("TABLE_NAME") or "fact-check-results"

dynamodb = session.resource("dynamodb")

FactCheckOutput = Literal["accurate", "inaccurate", "false", "indeterminate"]
Status = Union[Literal["pending"], FactCheckOutput]


class Task(BaseModel):
    task_id: str
    text: str
    result: Status


def update_task(task: Task):
    table = dynamodb.Table(TABLE_NAME)
    return table.put_item(Item=task.model_dump())
