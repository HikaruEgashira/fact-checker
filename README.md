# Fact Checker

This project is an API server for performing fact-checking on given texts. When a text is received, it is sent to a queue as a fact-checking task. The fact-checking results are classified into four categories: accurate, inaccurate, false, and indeterminate. The results can be retrieved using the task ID.

## Setup and Run

### Prerequisites

- Python 3.8 or higher
- AWS account
- AWS CLI configured with your credentials

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/HikaruEgashira/fact-checker.git
   cd fact-checker
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Deploy the infrastructure using Terraform:
   ```sh
   cd infrastructure/terraform
   terraform init
   terraform apply
   ```

### Running the API Server

To run the API server locally, use the following command:
```sh
python src/app.py
```

## API Documentation

### Endpoints

#### POST /fact-check

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

#### GET /fact-check/{task_id}

- **Description**: Retrieve the fact-checking result for a given task ID.
- **Response**:
  ```json
  {
    "task_id": "unique-task-id",
    "result": "accurate" | "inaccurate" | "false" | "indeterminate"
  }
  ```

## CLI Usage

### Submit a Fact-Checking Request

To submit a fact-checking request via the CLI, use the following command:
```sh
python src/app.py submit --text "The text to be fact-checked."
```

### Check Task Status

To check the status of a fact-checking task via the CLI, use the following command:
```sh
python src/app.py status --task_id "unique-task-id"
```

## Log

```sh
LOG_GROUP_NAME="/aws/lambda/fact_check_handler"
LOG_STREAM_NAME=$(aws logs describe-log-streams --log-group-name $LOG_GROUP_NAME --query 'logStreams[0].logStreamName' --output text)
aws logs get-log-events --log-group-name $LOG_GROUP_NAME --log-stream-name $LOG_STREAM_NAME
```
