import json
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import (
    APIGatewayProxyEvent,
    event_source,
)

from schemas.state import State, update_state, get_state
from schemas.command import FactcheckCommand, send_command

logger = Logger()


def enqueue_fact_check_state(state_id: str, prompt: str):
    # Save the state to DynamoDB
    state = State(id=state_id, status="pending", output="")
    update_state(state)

    # Send the state to the queue
    command = FactcheckCommand(prompt=prompt)
    send_command(command)

    return {
        "statusCode": 200,
        "body": state.model_dump_json(),
    }


def check_state_status(state_id: str):
    state = get_state(state_id)
    if state:
        return {"statusCode": 200, "body": state.model_dump_json()}
    else:
        body = {"error": "State not found"}
        return {"statusCode": 404, "body": json.dumps(body)}


@logger.inject_lambda_context
@event_source(data_class=APIGatewayProxyEvent)
def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    logger.info(f"Received event: {event}")
    if event.http_method == "POST" and event.path == "/fact-check":
        prompt = json.loads(event["body"])["prompt"]
        return enqueue_fact_check_state(context.aws_request_id, prompt)
    elif event.http_method == "GET" and event.path.startswith("/fact-check/"):
        state_id = event.path.split("/")[-1]
        return check_state_status(state_id)
    else:
        body = {"error": "Invalid request"}
        return {"statusCode": 400, "body": json.dumps(body)}
