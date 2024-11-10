import boto3
from aws_lambda_powertools.logging import Logger
from typing import Literal
from schemas.state import current_session

bedrock = boto3.client("bedrock-runtime", "us-west-2")
logger = Logger()


class FactCheck:
    @classmethod
    def run(
        cls, prompt: str
    ) -> Literal["accurate", "inaccurate", "false", "indeterminate"]:
        response = bedrock.converse(
            modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
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
                    "content": [{"text": prompt}],
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
        if output not in ["accurate", "inaccurate", "false", "indeterminate"]:
            logger.warning(f"Invalid response: {current_session()} {output}")
            return "indeterminate"

        return output  # type: ignore
