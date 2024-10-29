output "api_endpoint" {
  description = "The endpoint for the FactCheckAPI"
  value       = aws_api_gateway_deployment.fact_check_api_deployment.invoke_url
}
