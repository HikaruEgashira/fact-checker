import unittest
import json
from typing import Dict, Any
from app import handle_request, check_task_status, submit_fact_check_request, check_fact_check_status

class TestApp(unittest.TestCase):

    def test_handle_request(self, event: Dict[str, Any], context: Any) -> None:
        event = {
            'body': json.dumps({'text': 'The text to be fact-checked.'})
        }
        context = {}
        response = handle_request(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('task_id', json.loads(response['body']))

    def test_check_task_status(self, event: Dict[str, Any], context: Any) -> None:
        event = {
            'pathParameters': {'task_id': 'unique-task-id'}
        }
        context = {}
        response = check_task_status(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('result', json.loads(response['body']))

    def test_submit_fact_check_request(self, text: str) -> None:
        response = submit_fact_check_request('The text to be fact-checked.')
        self.assertIn('task_id', response)

    def test_check_fact_check_status(self, task_id: str) -> None:
        response = check_fact_check_status('unique-task-id')
        self.assertIn('result', response)

if __name__ == '__main__':
    unittest.main()
