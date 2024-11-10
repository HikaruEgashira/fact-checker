import boto3
from aws_lambda_powertools.logging import Logger
from typing import Literal
import os

bedrock_agent = boto3.client("bedrock-agent-runtime", "us-west-2")
bedrock_agent_core = boto3.client("bedrock-agent", "us-west-2")
logger = Logger()


class FactCheck:
    """
    https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/agents/MLEE4EGAPK
    """

    agent_id = os.environ.get("FACT_CHECK_AGENT_ID") or "ML3E4EGAPK"
    alias_id = os.environ.get("FACT_CHECK_ALIAS_ID") or "T12USSQNST"

    @classmethod
    def run(
        cls, session_id: str, prompt: str
    ) -> Literal["accurate", "inaccurate", "false", "indeterminate"]:
        response = bedrock_agent.invoke_agent(
            inputText=prompt,
            agentId=cls.alias_id,
            agentAliasId=cls.alias_id,
            sessionId=session_id,
        )

        output = (
            response.get("output", {})
            .get("message", {})
            .get("content", [{}])[0]
            .get("text", "")
        )
        if output not in ["accurate", "inaccurate", "false", "indeterminate"]:
            logger.warning(f"Invalid response: {session_id} {output}")
            return "indeterminate"

        return output
