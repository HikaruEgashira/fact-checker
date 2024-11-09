import json
from time import sleep
from aws_lambda_powertools.utilities.typing import LambdaContext

from lambda_api import (
    enqueue_fact_check_state,
    check_state_status,
)
from schemas.state import delete_state


context = LambdaContext()
context._aws_request_id = "unique-request-id"


def test_api(snapshot):
    state = "The text to be fact-checked."
    enqueue_response = enqueue_fact_check_state(state, context)
    assert "id" in enqueue_response["body"]
    state_id = json.loads(enqueue_response["body"])["id"]
    check_response = {}
    retry = 10
    while retry > 0:
        check_response = check_state_status(state_id, context)
        if json.loads(check_response["body"])["result"] != "pending":
            break
        sleep(1)
        retry -= 1
    assert check_response["statusCode"] == 200
    assert check_response == snapshot

    delete_state(state_id)
