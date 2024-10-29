import unittest
from queue import send_task_to_queue, retrieve_task_result

class TestQueue(unittest.TestCase):

    def test_send_task_to_queue(self):
        task_id = send_task_to_queue('The text to be fact-checked.')
        self.assertIsNotNone(task_id)

    def test_retrieve_task_result(self):
        task_id = send_task_to_queue('The text to be fact-checked.')
        result = retrieve_task_result(task_id)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
