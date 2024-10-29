import pytest
from queue_manager import send_task_to_queue, retrieve_task_result

def test_send_task_to_queue(text: str) -> None:
    task_id = send_task_to_queue('The text to be fact-checked.')
    assert task_id is not None

def test_retrieve_task_result(task_id: str) -> None:
    task_id = send_task_to_queue('The text to be fact-checked.')
    result = retrieve_task_result(task_id)
    assert result is not None
