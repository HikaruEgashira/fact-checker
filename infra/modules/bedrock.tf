provider "aws" {
  region = "us-west-2"
  alias  = "us-west-2"
}

resource "aws_bedrockagent_agent" "factcheck_actor" {
  provider                    = aws.us-west-2
  agent_name                  = "factcheck-actor-staging_${var.stage}"
  agent_resource_role_arn     = aws_iam_role.bedrock_agent_role.arn
  foundation_model            = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
  idle_session_ttl_in_seconds = 600
  instruction                 = <<EOF
task: 次の文章をファクトチェックし結果のみ出力してください。

output format: "accurate" | "inaccurate" | "false" | "indeterminate"
example1: "Yesterday was Monday." → "indeterminate"
example2: "The text to be fact-checked." → "accurate"
example3: "The moon is made of cheese." → "false"
example4: "The earth is flat." → "inaccurate"
example5: "The earth is round." → "accurate"
EOF
}

resource "aws_bedrockagent_agent_alias" "factcheck_actor" {
  provider         = aws.us-west-2
  agent_alias_name = "factcheck-actor-${var.stage}-0-0-1"
  agent_id         = aws_bedrockagent_agent.factcheck_actor.id
}

resource "aws_iam_role" "bedrock_agent_role" {
  name = "AmazonBedrockExecutionRoleForAgents_${var.stage}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AmazonBedrockAgentBedrockFoundationModelPolicyProd"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:bedrock:us-west-2:${data.aws_caller_identity.current.account_id}:agent/*"
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "bedrock_agent_policy" {
  name        = "AmazonBedrockAgentPolicy_${var.stage}"
  description = "Policy for Bedrock Agent to invoke foundation models"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AmazonBedrockAgentBedrockFoundationModelPolicyProd"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:us-west-2:${data.aws_caller_identity.current.account_id}:inference-profile/us.anthropic.claude-3-5-haiku-20241022-v1:0"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel*",
          "bedrock:CreateInferenceProfile"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*",
          "arn:aws:bedrock:*:*:inference-profile/*",
          "arn:aws:bedrock:*:*:application-inference-profile/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:GetInferenceProfile",
          "bedrock:ListInferenceProfiles",
          "bedrock:DeleteInferenceProfile",
          "bedrock:TagResource",
          "bedrock:UntagResource",
          "bedrock:ListTagsForResource"
        ]
        Resource = [
          "arn:aws:bedrock:*:*:inference-profile/*",
          "arn:aws:bedrock:*:*:application-inference-profile/*"
        ]
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "bedrock_agent_role_policy_attachment" {
  role       = aws_iam_role.bedrock_agent_role.name
  policy_arn = aws_iam_policy.bedrock_agent_policy.arn
}

resource "aws_iam_role_policy_attachment" "bedrock_full_access" {
  role       = aws_iam_role.bedrock_agent_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}
