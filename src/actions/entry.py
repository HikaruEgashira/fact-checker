from schemas.state import State, update_state, current_session
from schemas.command import EntryCommand
from agents.fact_check import FactCheck


def entry_action(command: EntryCommand):
    response = FactCheck().run(command.prompt)

    state = State(
        id=current_session(),
        status="completed",
        output=response,
    )
    update_state(state)
