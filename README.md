# EDS Data Plane Module for EC2
This module enables automatic registration of your service endpoints to Verizon's edge discovery service using AWS tags.

## Getting Started
To launch this module, clone the repo and initialize the Terraform module.
```
terraform init
```

Next, edit `terraform.tfvars` to populate your EDS key pair and, most importantly, `applicationName`. You will use this value as the tag for any EC2-based resources that you intend to launch in this region.
```
terraform apply -auto-approve 
```

## Launching Infrastructure
For any EC2 instances launched thereafter, be sure to use the following Tag for each resource:

```
Key: eds-ec2-plugin-app-name
Value: <applicationName> #The value you set to the applicationName variable in terraform.tfvars  
```

Note that, by default, this tag value is set to `wavelength-app`.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | 3.51.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 3.51.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.ec2_event_rule](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.lambdaTarget](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_role.iam_for_lambda](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.iam_for_lambda_ec2Access](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.iam_for_lambda_ssmAccess](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/iam_role_policy_attachment) | resource |
| [aws_lambda_function.edsDataPlaneLambda](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.allow_cloudwatch_to_call_lambda](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/lambda_permission) | resource |
| [aws_ssm_parameter.eds-data-plane-api-applicationName](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.eds-data-plane-api-edsAccessKey](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.eds-data-plane-api-edsSecretKey](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.eds-data-plane-api-edsServiceEndpointsId](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.eds-data-plane-api-edsServiceProfileId](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/ssm_parameter) | resource |
| [aws_ssm_parameter.eds-data-plane-api-portNumber](https://registry.terraform.io/providers/hashicorp/aws/3.51.0/docs/resources/ssm_parameter) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_applicationName"></a> [applicationName](#input\_applicationName) | Tag value that AWS API will search for to populate your Edge Discovery Service endpoints (the tag key must read 'eds-ec2-plugin-app-name'). | `string` | `"wavelength-app"` | no |
| <a name="input_edsAccessKey"></a> [edsAccessKey](#input\_edsAccessKey) | The access key for the Verizon Edge Discovery Service | `string` | n/a | yes |
| <a name="input_edsSecretKey"></a> [edsSecretKey](#input\_edsSecretKey) | The access key for the Verizon Edge Discovery Service | `string` | n/a | yes |
| <a name="input_edsServiceEndpointsId"></a> [edsServiceEndpointsId](#input\_edsServiceEndpointsId) | The serviceEndpointsId maintained by the Verizon Edge Discovery Service | `string` | n/a | yes |
| <a name="input_edsServiceProfileId"></a> [edsServiceProfileId](#input\_edsServiceProfileId) | The serviceProfileId maintained by the Verizon Edge Discovery Service | `string` | n/a | yes |
| <a name="input_portNumber"></a> [portNumber](#input\_portNumber) | The port number of your application service maintained by the Verizon Edge Discovery Service | `string` | `"80"` | no |
| <a name="input_profile"></a> [profile](#input\_profile) | The name of your AWS crendential profile, found most often in ~/.aws/credentials | `string` | `"default"` | no |
| <a name="input_region"></a> [region](#input\_region) | The AWS region to deploy your Wavelength configuration. | `string` | `"us-east-1"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->