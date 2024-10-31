from typing import Any, Dict
import argparse
import json
from src.fetch_handler import lambda_handler


def submit_fact_check_request(text: str) -> Dict[str, Any]:
    evevt = {
        "path": "/fact-check",
        "httpMethod": "POST",
        "body": json.dumps({"text": text}),
    }
    return lambda_handler(evevt, None)  # type: ignore


def check_fact_check_status(task_id: str) -> Dict[str, Any]:
    event = {
        "path": f"/fact-check/{task_id}",
        "httpMethod": "GET",
        "pathParameters": {"task_id": task_id},
    }
    return lambda_handler(event, None)  # type: ignore


def main() -> None:
    parser = argparse.ArgumentParser(description="Fact Checker CLI")
    subparsers = parser.add_subparsers(dest="command")

    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--text", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--task_id", required=True, help="The task ID")

    args = parser.parse_args()

    if args.command == "submit":
        result = submit_fact_check_request(args.text)
        print(result)
    elif args.command == "status":
        result = check_fact_check_status(args.task_id)
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
