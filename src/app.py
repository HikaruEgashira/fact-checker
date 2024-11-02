import argparse
from lambda_api import enqueue_fact_check_task, check_task_status
from aws_lambda_powertools.utilities.typing import LambdaContext
import uuid


def main():
    context = LambdaContext()
    context._aws_request_id = str(uuid.uuid4())

    parser = argparse.ArgumentParser(description="Fact Checker CLI")
    subparsers = parser.add_subparsers(dest="command")

    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--text", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--task_id", required=True)

    args = parser.parse_args()
    match args.command:
        case "submit":
            print(enqueue_fact_check_task(args.text, context))
        case "status":
            print(check_task_status(args.task_id, context))
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
