from schemas.state import State, update_state
from schemas.command import EntryCommand
from agents.fact_check import FactCheck


def entry_action(command: EntryCommand):
    response = FactCheck().run(command.id, command.prompt)

    state = State(
        id=command.id,
        status="completed",
        output=response,
    )
    update_state(state)
