# API Endpoints

## POST /fact-check

- **Description**: Submit a prompt for fact-checking.
- **Request Body**:
  ```json
  {
    "prompt": "The prompt to be fact-checked."
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
    "result": "accurate" | "almost accurate" | "misleading" | "inaccurate" | "unsupported" | "incorrect" | "false" | "indeterminate" | "out of scope"
  }
  ```
