import boto3
from aws_lambda_powertools import Logger
from schemas.state import State, update_state, Status
from schemas.command import EntryCommand

# Initialize AWS clients
bedrock = boto3.client("bedrock-runtime")
logger = Logger()


def entry_command(command: EntryCommand):
    response = bedrock.converse(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": """
                            task: 次の文章をファクトチェックし結果のみ出力してください。
                            output format: "accurate" | "inaccurate" | "false" | "indeterminate"
                            example1: "Yesterday was Monday." → "indeterminate"
                            example2: "The text to be fact-checked." → "accurate"
                            example3: "The moon is made of cheese." → "false"
                            example4: "The earth is flat." → "inaccurate"
                            example5: "The earth is round." → "accurate"
                        """
                    }
                ],
            },
            {"role": "assistant", "content": [{"text": "accurate"}]},
            {
                "role": "user",
                "content": [{"text": command.text}],
            },
        ],
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )
    response_text: Status = response["output"]["message"]["content"][0]["text"]  # type: ignore
    if response_text not in ["accurate", "inaccurate", "false", "indeterminate"]:
        raise ValueError(f"Invalid response: {response_text}")

    logger.info(f"Received response: {response_text}")
    state = State(
        id=command.id,
        result=response_text,
    )
    update_state(state)
