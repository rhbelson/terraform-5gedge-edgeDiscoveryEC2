output "edsServiceProfileId" {
  value       = aws_ssm_parameter.eds-data-plane-api-edsServiceProfileId.value
  # sensitive   = true
  description = "This is the edge discovery service (EDS) service profile ID created by the module."
}

output "edsServiceEndpointsId" {
  value       = aws_ssm_parameter.eds-data-plane-api-edsServiceEndpointsId.value
  # sensitive   = true
  description = "This is the edge discovery service (EDS) serviceEndpointsId that you will use to retrieve endpoints."
}
