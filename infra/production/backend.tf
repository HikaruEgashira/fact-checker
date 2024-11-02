provider "aws" {
  region = var.aws_region
}

terraform {
  backend "s3" {
    bucket = "hikae-terraform"
    key    = "fact-checker/production/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

module "production" {
  source              = "../modules"
  aws_region          = var.aws_region
  dynamodb_table_name = var.dynamodb_table_name
  queue_name          = var.queue_name
  stage               = var.stage
}
