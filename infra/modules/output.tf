output "api_endpoint" {
  value = aws_api_gateway_stage.fact_checker_api_stage.invoke_url
}

output "agent_id" {
  value = aws_bedrockagent_agent.factcheck_actor.id
}

output "agent_alias_id" {
  value = aws_bedrockagent_agent_alias.factcheck_actor.agent_alias_id
}
