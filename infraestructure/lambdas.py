import os
import json
import pulumi
import pulumi_aws as aws

from itertools import chain

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
scripts = [
    os.path.splitext(f)[0] for f in os.listdir("../scraping") if f.endswith(".py")
]
for s in scripts:
    file_path = f"../scraping/{s}.py"
    lambdas[s] = aws.lambda_.Function(
        s,
        name=s,
        role=lambda_role.arn,
        runtime=aws.lambda_.Runtime.PYTHON3D12,
        code=pulumi.FileArchive("../scraping"),
        handler=f"{s}.lambda_handler",
    )
