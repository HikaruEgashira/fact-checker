import json
from time import sleep

from lambda_api import (
    enqueue_fact_check_state,
    check_state_status,
)
from schemas.state import State, delete_state


def test_api(snapshot):
    state_id = "unique-request-id"
    prompt = "The text to be fact-checked."

    enqueue_response = enqueue_fact_check_state(state_id, prompt)
    assert "id" in enqueue_response["body"]
    assert state_id == json.loads(enqueue_response["body"])["id"]

    retry = 10
    state: State | None = None
    while retry > 0:
        check_response = check_state_status(state_id)
        assert check_response["statusCode"] == 200
        state = State(**json.loads(check_response["body"]))
        if state.status == "completed":
            break

        print("Waiting for state to complete...")
        sleep(1)
        retry -= 1

    assert state is not None
    assert state.status == "completed"
    assert state.model_dump_json() == snapshot
    delete_state(state_id)
