import argparse
import uuid

from schemas.command import FactcheckCommand, send_command
from schemas.state import State, update_state


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
            # Save the state to DynamoDB
            state = State(id=args.id, status="pending", output="")
            update_state(state)

            # Send the state to the queue
            command = FactcheckCommand(prompt=args.prompt)
            send_command(command)

            print(state)
            return
        case "state":
            state = State(id=args.id, status="pending", output="")
            print(state)
            return
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
