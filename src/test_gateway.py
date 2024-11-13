from time import sleep
import urllib3
import json
import os

from schemas.state import State

API_ENDPOINT = os.environ.get("API_ENDPOINT")
if not API_ENDPOINT:
    raise ValueError("API_ENDPOINT environment variable is required")


def test_gateway(snapshot):
    http = urllib3.PoolManager()

    # POST /fact-check
    data = {"prompt": "The earth is round."}
    response = http.request(
        "POST",
        f"{API_ENDPOINT}/fact-check",
        body=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    assert response.status == 200

    response_json = json.loads(response.data.decode("utf-8"))
    state = State(**response_json)

    assert state.status == "pending"
    state.id = "***"
    assert state.model_dump_json() == snapshot(name="POST /fact-check")

    # GET /fact-check/{id}
    state_id = json.loads(response.data)["id"]
    retry = 10
    state: State | None = None
    while retry > 0:
        response = http.request("GET", f"{API_ENDPOINT}/fact-check/{state_id}")
        response_json = json.loads(response.data.decode("utf-8"))
        state = State(**response_json)
        if state.status == "completed":
            break

        print("Waiting for state to complete...")
        sleep(3)
        retry -= 1
    assert response.status == 200

    assert state is not None
    assert state.status == "completed"
    state.id = "***"
    assert state.model_dump_json() == snapshot(name="GET /fact-check/{id}")
