provider "aws" {
  profile = var.profile
  region  = var.region
}

###########################################################################
# Create SSM Parameters for Lambda Function
resource "aws_ssm_parameter" "eds-data-plane-api-applicationName" {
  name  = "eds-data-plane-api-applicationName"
  type  = "String"
  value = var.applicationName
}

resource "aws_ssm_parameter" "eds-data-plane-api-edsAccessKey" {
  name  = "eds-data-plane-api-edsAccessKey"
  type  = "String"
  value = var.edsAccessKey
}

resource "aws_ssm_parameter" "eds-data-plane-api-edsSecretKey" {
  name  = "eds-data-plane-api-edsSecretKey"
  type  = "String"
  value = var.edsSecretKey
}

resource "aws_ssm_parameter" "eds-data-plane-api-portNumber" {
  name  = "eds-data-plane-api-portNumber"
  type  = "String"
  value = var.portNumber
}

resource "aws_ssm_parameter" "eds-data-plane-api-edsServiceProfileId" {
  name  = "eds-data-plane-api-edsServiceProfileId"
  type  = "String"
  value = var.edsServiceProfileId
}

resource "aws_ssm_parameter" "eds-data-plane-api-edsServiceEndpointsId" {
  name  = "eds-data-plane-api-edsServiceEndpointsId"
  type  = "String"
  value = var.edsServiceEndpointsId
}
#############################################################################33

#Lambda Function Components
resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "iam_for_lambda_ec2Access" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

resource "aws_iam_role_policy_attachment" "iam_for_lambda_ssmAccess" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}

resource "aws_lambda_function" "edsDataPlaneLambda" {
  function_name    = "edsDataPlaneLambda"
  role             = aws_iam_role.iam_for_lambda.arn
  handler          = "index.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/edsDataPlaneLambda.zip")
  runtime          = "python3.8"
  timeout          = 10
  environment {
    variables = {
      foo = "bar"
    }
  }
}
#######################################################################################
#EventBridge Assets
resource "aws_cloudwatch_event_rule" "ec2_event_rule" {
  name        = "carrier_ip_creation_or_ec2_creation"
  description = "Event for EDS Data Plane API"
  # role_arn      = aws_iam_role.iam_for_lambda.arn
  event_pattern = <<EOF
    {
    "source": ["aws.ec2"],
      "detail-type": [ "EC2 Instance State-change Notification" ],
      "detail": {
      "state": ["running", "terminated"]
      }
    }
  EOF
}

resource "aws_cloudwatch_event_target" "lambdaTarget" {
  rule      = aws_cloudwatch_event_rule.ec2_event_rule.name
  target_id = aws_lambda_function.edsDataPlaneLambda.function_name
  arn       = aws_lambda_function.edsDataPlaneLambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.edsDataPlaneLambda.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_event_rule.arn
}
