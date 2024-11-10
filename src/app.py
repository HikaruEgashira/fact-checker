import argparse
from lambda_api import enqueue_fact_check_state, check_state_status
from aws_lambda_powertools.utilities.typing import LambdaContext
import uuid


def main():
    context = LambdaContext()
    context._aws_request_id = str(uuid.uuid4())

    parser = argparse.ArgumentParser(description="Fact Checker CLI")
    subparsers = parser.add_subparsers(dest="command")

    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--text", required=True)

    status_parser = subparsers.add_parser("state")
    status_parser.add_argument("--state-id", required=True)

    args = parser.parse_args()
    match args.command:
        case "submit":
            print(enqueue_fact_check_state(args.state_id, args.text))
            return
        case "state":
            print(check_state_status(args.state_id))
            return
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
