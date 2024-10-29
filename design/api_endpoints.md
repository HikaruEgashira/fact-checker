# API Endpoints

## POST /fact-check

- **Description**: Submit a text for fact-checking.
- **Request Body**:
  ```json
  {
    "text": "The text to be fact-checked."
  }
  ```
- **Response**:
  ```json
  {
    "task_id": "unique-task-id"
  }
  ```

## GET /fact-check/{task_id}

- **Description**: Retrieve the fact-checking result for a given task ID.
- **Response**:
  ```json
  {
    "task_id": "unique-task-id",
    "result": "accurate" | "inaccurate" | "false" | "indeterminate"
  }
  ```
