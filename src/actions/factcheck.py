from agents.factcheck_opponent import reflect_factcheck
from schemas.state import State, update_state, current_session
from schemas.command import FactcheckCommand
from agents.factcheck_agent import extract_factcheck_result, invoke_factcheck_agent
from aws_lambda_powertools.logging import Logger

logger = Logger()


def factcheck_action(command: FactcheckCommand):
    logger.info(f"Fact-checking: {command.prompt}")
    state_id = current_session()
    state = State(id=state_id, status="running", output="")
    update_state(state)

    rounds = 1
    response = invoke_factcheck_agent(command.prompt)
    logger.info(f"Round {rounds} agent   : {response}")
    for _ in range(rounds):
        opponent_response = reflect_factcheck(response)
        logger.info(f"Round {rounds} opponent: {opponent_response}")
        reflect = f"""
            {"\n".join(map(lambda x: f"> {x}", response.splitlines()))}
            この返答に対して以下のように反論がありました。
            {opponent_response}
            この反論を踏まえて再度ファクトチェックを行ってください。
            最後の行はプログラムで処理するので結果以外の情報は含めないでください。
            """

        response = invoke_factcheck_agent(reflect)
        logger.info(f"Round {rounds} agent   : {response}")

    output = extract_factcheck_result(response)
    state = State(id=state_id, status="completed", output=output)
    return state
