import json
import pytest
from src.fetch_handler import (
    enqueue_fact_check_task,
    check_task_status,
)


def test_handle_request():
    event = {"body": json.dumps({"text": "The text to be fact-checked."})}
    context = {}
    response = enqueue_fact_check_task(event, context)  # type: ignore
    assert response["statusCode"] == 200
    assert "task_id" in json.loads(response["body"])


def test_check_task_status():
    event = {"pathParameters": {"task_id": "unique-task-id"}}
    context = {}
    response = check_task_status(event, context)  # type: ignore
    assert response["statusCode"] == 404
