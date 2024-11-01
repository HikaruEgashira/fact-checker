variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "ap-northeast-1"
}

variable "queue_name" {
  description = "The name of the SQS queue"
  type        = string
  default     = "fact-checker-queue"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table for storing fact-check results"
  type        = string
  default     = "fact-checker-results"
}
