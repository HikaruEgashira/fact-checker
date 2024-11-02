output "api_endpoint" {
  value = aws_api_gateway_deployment.fact_checker_api_deployment.invoke_url
}
