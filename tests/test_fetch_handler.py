import unittest
import json
from typing import Dict, Any
from src.fetch_handler import (
    enqueue_fact_check_task,
    check_task_status,
)


class TestApp(unittest.TestCase):
    def test_handle_request(self) -> None:
        event = {"body": json.dumps({"text": "The text to be fact-checked."})}
        context = {}
        response = enqueue_fact_check_task(event, context)  # type: ignore
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("task_id", json.loads(response["body"]))

    def test_check_task_status(self) -> None:
        event = {"pathParameters": {"task_id": "unique-task-id"}}
        context = {}
        response = check_task_status(event, context)  # type: ignore
        self.assertEqual(response["statusCode"], 404)


if __name__ == "__main__":
    unittest.main()
