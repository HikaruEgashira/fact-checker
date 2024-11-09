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
    "id": "unique-state-id"
  }
  ```

## GET /fact-check/{id}

- **Description**: Retrieve the fact-checking result for a given state ID.
- **Response**:
  ```json
  {
    "id": "unique-state-id",
    "result": "accurate" | "inaccurate" | "false" | "indeterminate"
  }
  ```
