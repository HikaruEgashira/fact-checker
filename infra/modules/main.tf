resource "aws_sqs_queue" "fact_checker_queue" {
  name = var.queue_name
}

resource "aws_dynamodb_table" "fact_checker_results" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role_${var.stage}"

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
  name = "lambda_policy_${var.stage}"

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
  source_dir  = "../../src"
  output_path = "../../package-${var.stage}.zip"
  excludes    = ["__snapshots__"]
}

resource "aws_lambda_function" "fact_checker_api" {
  function_name    = "fact_checker_api_${var.stage}"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_api.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.deployment_package.output_path
  source_code_hash = filebase64sha256(data.archive_file.deployment_package.output_path)

  layers = [
    "arn:aws:lambda:${var.aws_region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:2"
  ]

  logging_config {
    log_group  = "/fact_checker_${var.stage}"
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
  function_name    = "fact_checker_worker_${var.stage}"
  role             = aws_iam_role.lambda_execution_role.arn
  handler          = "lambda_worker.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.deployment_package.output_path
  source_code_hash = filebase64sha256(data.archive_file.deployment_package.output_path)

  layers = [
    "arn:aws:lambda:${var.aws_region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:2"
  ]

  logging_config {
    log_group  = "/fact_checker_${var.stage}"
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
  name              = "/fact_checker_${var.stage}"
  retention_in_days = 30
}

# API Gateway

resource "aws_api_gateway_rest_api" "fact_checker_api" {
  name        = "fact_checker_api_${var.stage}"
  description = "fact-checker API"
  body = templatefile("${path.module}/openapi.yaml", {
    aws_region_name     = var.aws_region
    lambda_function_arn = aws_lambda_function.fact_checker_api.arn
    stage               = var.stage
  })
}

resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fact_checker_api.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.fact_checker_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "fact_checker_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.fact_checker_api.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.fact_checker_api.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "fact_checker_api_stage" {
  stage_name    = var.stage
  rest_api_id   = aws_api_gateway_rest_api.fact_checker_api.id
  deployment_id = aws_api_gateway_deployment.fact_checker_api_deployment.id
}
