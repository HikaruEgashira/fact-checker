output "api_endpoint" {
  value = aws_api_gateway_deployment.fact_check_api_deployment.invoke_url
}
