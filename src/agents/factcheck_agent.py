import boto3
from aws_lambda_powertools.logging import Logger
from typing import Literal

bedrock = boto3.client("bedrock-runtime", "us-west-2")
logger = Logger()

agent = """task: 次の文章をファクトチェックし最後の行に結果を返答してください。
結果を答える前に根拠を説明すること。100字程度で回答してください。

output format: "accurate" | "inaccurate" | "false" | "indeterminate"
<example1>
    <input>Yesterday was Monday.
    <output>
        今日が何日であるかコンテキストがないため今日がTuesdayであるかどうか判断不能
        indeterminate
    </output>
</example1>
<example2>
    <input>The moon is made of cheese.
    <output>
        月がチーズでできているという科学的根拠がない
        false
    </output>
</example2>
<example3>
    <input>The earth is flat.
    <output>
        地球は球体であるという科学的根拠がある
        inaccurate
    </output>
</example3>
<example4>
    <input>The earth is round.
    <output>
        地球が球体であるという科学的根拠がある
        accurate
    </output>
</example4>
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
) -> Literal["accurate", "inaccurate", "false", "indeterminate"]:
    if "accurate" in output:
        return "accurate"
    elif "inaccurate" in output:
        return "inaccurate"
    elif "false" in output:
        return "false"
    elif "indeterminate" in output:
        return "indeterminate"
    else:
        return "indeterminate"
