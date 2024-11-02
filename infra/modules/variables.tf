variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
}

variable "queue_name" {
  description = "The name of the SQS queue"
  type        = string
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table for storing fact-check results"
  type        = string
}

variable "stage" {
  type = string
}
