output "api_endpoint" {
  value = aws_api_gateway_stage.fact_checker_api_stage.invoke_url
}
