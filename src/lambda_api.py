from pydantic import BaseModel
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from schemas.state import State, update_state, get_state
from schemas.command import FactcheckCommand, send_command

tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver(enable_validation=True)


class FactCheckRequest(BaseModel):
    prompt: str


class FactCheckState(BaseModel):
    id: str
    status: str
    output: str


@app.post("/fact-check")
@tracer.capture_method
def enqueue_fact_check() -> FactCheckState:
    body = app.current_event.json_body
    prompt = body["prompt"]
    state_id = app.current_event.request_context.request_id

    # Save the state to DynamoDB
    state = State(id=state_id, status="pending", output="")
    update_state(state)

    # Send the state to the queue
    command = FactcheckCommand(prompt=prompt)
    send_command(command)

    return FactCheckState(id=state_id, status="pending", output="")


@app.get("/fact-check/<state_id>")
@tracer.capture_method
def check_state(state_id: str) -> FactCheckState:
    state = get_state(state_id)
    if state:
        return FactCheckState(id=state.id, status=state.status, output=state.output)
    else:
        raise Exception("State not found")


@app.exception_handler(Exception)
def handle_exception(ex: Exception):
    logger.error(ex)
    return Response(status_code=404)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
