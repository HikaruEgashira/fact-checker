import argparse
from lambda_api import enqueue_fact_check_state, check_state_status
import uuid


def main():
    parser = argparse.ArgumentParser(description="Fact Checker CLI")
    subparsers = parser.add_subparsers(dest="command")

    submit_parser = subparsers.add_parser("submit")
    submit_parser.add_argument("--prompt", required=True)
    submit_parser.add_argument("--id", default=str(uuid.uuid4()))

    status_parser = subparsers.add_parser("state")
    status_parser.add_argument("--id", required=True)

    args = parser.parse_args()
    match args.command:
        case "submit":
            print(enqueue_fact_check_state(args.id, args.text))
            return
        case "state":
            if args.id is None:
                print("Please provide a state id")
                return
            print(check_state_status(args.id))
            return
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
