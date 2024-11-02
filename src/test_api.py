import json
from time import sleep
from lambda_api import (
    enqueue_fact_check_task,
    check_task_status,
)
from aws_lambda_powertools.utilities.typing import LambdaContext

context = LambdaContext()


def test_handle_request(snapshot):
    text = "The text to be fact-checked."
    response = enqueue_fact_check_task(text, context)
    assert response["statusCode"] == 200
    assert response == snapshot


def test_check_task_status_failure(snapshot):
    task_id = "unique-task-id"
    response = check_task_status(task_id, context)
    assert response["statusCode"] == 404
    assert response == snapshot


def test_check_task_status_success(snapshot):
    task = "The text to be fact-checked."
    enqueue_response = enqueue_fact_check_task(task, context)
    assert "task_id" in enqueue_response["body"]
    task_id = json.loads(enqueue_response["body"])["task_id"]
    check_response = {}
    retry = 10
    while retry > 0:
        check_response = check_task_status(task_id, context)
        if json.loads(check_response["body"])["result"] != "pending":
            break
        sleep(1)
        retry -= 1
    assert check_response["statusCode"] == 200
    assert check_response == snapshot
