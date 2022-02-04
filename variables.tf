variable "profile" {
  type        = string
  description = "The name of your AWS crendential profile, found most often in ~/.aws/credentials"
  default     = "default"
}

variable "region" {
  type        = string
  default     = "us-east-1"
  description = "The AWS region to deploy your Wavelength configuration."
  validation {
    condition     = contains(["us-east-1", "us-west-2"], var.region)
    error_message = "Valid values for regions supporting Wavelength Zones are us-east-1 and us-west-2."
  }
}

variable "edsAccessKey" {
  type        = string
  sensitive   = true
  description = "The access key for the Verizon Edge Discovery Service"
}

variable "edsSecretKey" {
  type        = string
  sensitive   = true
  description = "The access key for the Verizon Edge Discovery Service"
}

variable "edsServiceProfileId" {
  default     = ""
  type        = string
  description = "The serviceProfileId maintained by the Verizon Edge Discovery Service"
}

variable "edsServiceEndpointsId" {
  default     = ""
  type        = string
  description = "The serviceEndpointsId maintained by the Verizon Edge Discovery Service"
}

variable "portNumber" {
  type        = string
  default     = "80"
  description = "The port number of your application service maintained by the Verizon Edge Discovery Service"
}

variable "applicationName" {
  type        = string
  default     = "wavelength-app"
  description = "Tag value that AWS API will search for to populate your Edge Discovery Service endpoints (the tag key must read 'eds-ec2-plugin-app-name')."
}

