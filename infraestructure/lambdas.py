import os
import json
import pulumi
import pulumi_aws as aws

SCRAPING_DIRECTORY = "../scraping"  # TODO add it to the config yaml
lambda_role = aws.iam.Role(
    "lambda_role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        }
    ),
)

policy_statements = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
            ],
            "Resource": "arn:aws:logs:*:*:*",
        },
        # {
        #     "Effect": "Allow",
        #     "Action": [
        #         "ssm:GetParameters",
        #         "ssm:GetParameter",
        #         "ssm:GetParametersByPath",
        #         "ssm:PutParameter",
        #         "ssm:DeleteParameters"
        #     ],
        #     # "Resource": "arn:aws:ssm:us-east-2:123456789012:parameter/dbserver-prod-*"
        # },
        # {
        #     "Effect": "Allow",
        #     "Action": [
        #         "events:DescribeRule",
        #         "events:DisableRule",
        #         "events:EnableRule",
        #         "events:ListRules"
        #     ],
        #     # "Resource": "arn:aws:ssm:us-east-2:123456789012:parameter/dbserver-prod-*"
        # },
    ],
}
lambda_role_policy = aws.iam.RolePolicy(
    "lambda_role_policy", role=lambda_role.id, policy=json.dumps(policy_statements)
)

lambdas = {}
subdirectories = filter(
    os.path.isdir,
    [os.path.join(SCRAPING_DIRECTORY, f) for f in os.listdir(SCRAPING_DIRECTORY)],
)
for subdir in subdirectories:
    scripts = [os.path.splitext(f)[0] for f in os.listdir(subdir) if f.endswith(".py")]
    for script in scripts:
        lambdas[script] = aws.lambda_.Function(
            script,
            name=script,
            role=lambda_role.arn,
            runtime=aws.lambda_.Runtime.PYTHON3D12,
            code=pulumi.FileArchive(subdir),
            handler=f"{script}.lambda_handler",
        )
