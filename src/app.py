import argparse
from src.lambda_api import enqueue_fact_check_task, check_task_status
from aws_lambda_powertools.utilities.typing import LambdaContext


def main():
    context = LambdaContext()

    parser = argparse.ArgumentParser(description="Fact Checker CLI")
    subparsers = parser.add_subparsers(dest="command")

    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--text", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--task_id", required=True)

    args = parser.parse_args()
    match args.command:
        case "submit":
            enqueue_fact_check_task(args.text, context)
        case "status":
            check_task_status(args.task_id, context)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
