import boto3
from aws_lambda_powertools.logging import Logger
from typing import Literal

bedrock = boto3.client("bedrock-runtime", "us-west-2")
logger = Logger()


agent = """task: 次の文章をファクトチェックし最後の行に結果を返答してください。
結果を答える前に根拠を説明すること。100字程度で回答してください。

Judgement Criteria    Description
Accurate              No factual errors and no important elements are missing.
Almost Accurate       Some inaccuracies, but the main part/core is not wrong.
Misleading            Does not seem to be factually incorrect, but due to clickbait headlines or missing important elements, there is a high chance of misunderstanding.
Inaccurate            Contains both accurate and inaccurate parts, lacking overall accuracy.
Unsupported           Cannot be confirmed or proven, or there is very little evidence/support.
Incorrect             Contains factual errors in whole or in core parts.
False                 Contains factual errors in whole or in core parts, with a strong intention to convey as fact despite knowing it is not.
Indeterminate         Cannot be denied without strong possibility of further investigation/confirmation.
Out of Scope          Concerns opinions or subjective perceptions/evaluations, which cannot be proven or clarified for truth.

Input example                  Output example
Yesterday was Monday.          今日が何日であるかコンテキストがないため今日がTuesdayであるかどうか判断不能\nindeterminate
The moon is made of cheese.    月がチーズでできているという科学的根拠がない\nfalse
The earth is flat.             地球は球体であるという科学的根拠がある\ninaccurate
The earth is round.            地球が球体であるという科学的根拠がある\naccurate
"""


def invoke_factcheck_agent(prompt: str) -> str:
    response = bedrock.converse(
        modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": agent}, {"text": prompt}],
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


def extract_factcheck_result(
    output: str,
) -> Literal[
    "accurate",
    "almost accurate",
    "misleading",
    "inaccurate",
    "unsupported",
    "incorrect",
    "false",
    "indeterminate",
    "out of scope",
]:
    if "accurate" in output:
        return "accurate"
    elif "almost accurate" in output:
        return "almost accurate"
    elif "misleading" in output:
        return "misleading"
    elif "inaccurate" in output:
        return "inaccurate"
    elif "unsupported" in output:
        return "unsupported"
    elif "incorrect" in output:
        return "incorrect"
    elif "false" in output:
        return "false"
    elif "indeterminate" in output:
        return "indeterminate"
    elif "out of scope" in output:
        return "out of scope"
    else:
        return "unsupported"
