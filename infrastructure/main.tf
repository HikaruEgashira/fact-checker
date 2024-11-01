provider "aws" {
  region = var.aws_region
}

terraform {
  backend "s3" {
    bucket = "hikae-terraform"
    key    = "fact-checker/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

resource "aws_sqs_queue" "fact_checker_queue" {
  name = var.queue_name
}

resource "aws_dynamodb_table" "fact_checker_results" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "task_id"

  attribute {
    name = "task_id"
    type = "S"
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name = "lambda_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Effect   = "Allow"
        Resource = aws_sqs_queue.fact_checker_queue.arn
      },
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.fact_checker_results.arn
      },
      {
        Action = [
          "bedrock:InvokeModel"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "archive_file" "deployment_package" {
  type        = "zip"
  source_dir  = "../src"
  output_path = "../package.zip"
}

resource "aws_lambda_function" "fact_checker_api" {
  function_name    = "fact_checker_api"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "api.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.deployment_package.output_path
  source_code_hash = filebase64sha256(data.archive_file.deployment_package.output_path)

  layers = [
    "arn:aws:lambda:${var.aws_region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:2"
  ]

  logging_config {
    log_group  = "/fact_checker"
    log_format = "JSON"
  }

  environment {
    variables = {
      QUEUE_NAME = aws_sqs_queue.fact_checker_queue.name
      TABLE_NAME = aws_dynamodb_table.fact_checker_results.name
    }
  }
}

resource "aws_lambda_function" "fact_checker_worker" {
  function_name    = "fact_checker_worker"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "worker.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.deployment_package.output_path
  source_code_hash = filebase64sha256(data.archive_file.deployment_package.output_path)

  layers = [
    "arn:aws:lambda:${var.aws_region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:2"
  ]

  logging_config {
    log_group  = "/fact_checker"
    log_format = "JSON"
  }

  environment {
    variables = {
      QUEUE_NAME = aws_sqs_queue.fact_checker_queue.name
      TABLE_NAME = aws_dynamodb_table.fact_checker_results.name
    }
  }
}

resource "aws_lambda_event_source_mapping" "sqs_event_source" {
  event_source_arn = aws_sqs_queue.fact_checker_queue.arn
  function_name    = aws_lambda_function.fact_checker_worker.arn
  enabled          = true
  batch_size       = 10
}

resource "aws_cloudwatch_log_group" "fact_checker_handler" {
  name              = "/fact_checker"
  retention_in_days = 30
}

resource "aws_api_gateway_rest_api" "fact_checker_api" {
  name        = "FactCheckAPI"
  description = "API for fact-checking texts"
}

resource "aws_api_gateway_resource" "fact_checker_resource" {
  rest_api_id = aws_api_gateway_rest_api.fact_checker_api.id
  parent_id   = aws_api_gateway_rest_api.fact_checker_api.root_resource_id
  path_part   = "fact-check"
}

resource "aws_api_gateway_method" "post_fact_check" {
  rest_api_id   = aws_api_gateway_rest_api.fact_checker_api.id
  resource_id   = aws_api_gateway_resource.fact_checker_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "post_fact_checker_integration" {
  rest_api_id             = aws_api_gateway_rest_api.fact_checker_api.id
  resource_id             = aws_api_gateway_resource.fact_checker_resource.id
  http_method             = aws_api_gateway_method.post_fact_check.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.fact_checker_api.invoke_arn
}

resource "aws_api_gateway_method" "get_fact_checker_status" {
  rest_api_id   = aws_api_gateway_rest_api.fact_checker_api.id
  resource_id   = aws_api_gateway_resource.fact_checker_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_fact_checker_status_integration" {
  rest_api_id             = aws_api_gateway_rest_api.fact_checker_api.id
  resource_id             = aws_api_gateway_resource.fact_checker_resource.id
  http_method             = aws_api_gateway_method.get_fact_checker_status.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.fact_checker_api.invoke_arn
}

resource "aws_api_gateway_deployment" "fact_checker_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.post_fact_checker_integration,
    aws_api_gateway_integration.get_fact_checker_status_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.fact_checker_api.id
  stage_name  = "prod"
}
