import boto3
from aws_lambda_powertools.logging import Logger

bedrock = boto3.client("bedrock-runtime", "us-west-2")
logger = Logger()

reflect = """
You are an expert tasked with evaluating and providing feedback on an assistant's performance.
Please provide concise and constructive feedback. Remember, your role is similar to a teacher. Rather than giving away the solution or details about the answer, guide the assistant toward understanding how to arrive at the correct answer. Your feedback should focus on enhancing the assistant's ability to think critically and respond accurately.
"""


def reflect_factcheck(
    prompt: str,
) -> str:
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": reflect}, {"text": prompt}],
            },
        ],
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )

    output = (
        response.get("output", {})
        .get("message", {})
        .get("content", [{}])[0]
        .get("text", "")
    )
    return output
