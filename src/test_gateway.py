import urllib3
import json
import os

API_ENDPOINT = os.environ.get("API_ENDPOINT")
if not API_ENDPOINT:
    raise ValueError("API_ENDPOINT environment variable is required")


def test_gateway(snapshot):
    http = urllib3.PoolManager()

    # POST /fact-check
    data = {"prompt": "The text to be fact-checked."}
    response = http.request(
        "POST",
        f"{API_ENDPOINT}/fact-check",
        body=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    assert response.status == 200

    response_data = json.loads(response.data)
    response_data["id"] = "***"
    assert response_data == snapshot

    # GET /fact-check/{id}
    state_id = json.loads(response.data)["id"]
    retry = 10
    while retry > 0:
        response = http.request("GET", f"{API_ENDPOINT}/fact-check/{state_id}")
        if json.loads(response.data)["status"] != "pending":
            break
        retry -= 1
    assert response.status == 200

    response_data = json.loads(response.data)
    response_data["id"] = "***"
    assert response_data == snapshot
