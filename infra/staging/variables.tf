variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "ap-northeast-1"
}

variable "queue_name" {
  description = "The name of the SQS queue (staging)"
  type        = string
  default     = "fact-checker-queue-staging"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table for storing fact-check results (staging)"
  type        = string
  default     = "fact-checker-results-staging"
}

variable "stage" {
  type    = string
  default = "staging"
}
