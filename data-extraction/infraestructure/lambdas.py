import os
import json
import pulumi
import pulumi_aws as aws

from utils import scripts_subdirectories

AWS_ACCOUNT_ID = aws.get_caller_identity().account_id
AWS_REGION = aws.get_region().name

config = pulumi.Config()
pandas_layer_arn = config.require("pandasAWSLayerArn")

lambda_role = aws.iam.Role(
    "lambda_role",
    name="lambda_role",
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
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameters",
                "ssm:GetParameter",
                "ssm:GetParametersByPath",
                "ssm:PutParameter",
                "ssm:DeleteParameters",
            ],
            "Resource": f"arn:aws:ssm:{AWS_REGION}:{AWS_ACCOUNT_ID}:parameter/config/init_data_*",
        },
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
            "Resource": [
                "arn:aws:s3:::raw-recipe-data-bucket",
                "arn:aws:s3:::raw-recipe-data-bucket/*",
            ],
        },
        {
            "Effect": "Allow",
            "Action": ["scheduler:UpdateSchedule", "iam:PassRole"],
            "Resource": [
                f"arn:aws:scheduler:{AWS_REGION}:{AWS_ACCOUNT_ID}:schedule/default/schedule_rule_*"
            ],
        },
        {
            "Effect": "Allow",
            "Action": ["iam:PassRole"],
            "Resource": "*",
        },
    ],
}

lambda_role_policy = aws.iam.RolePolicy(
    "lambda_role_policy", role=lambda_role.id, policy=json.dumps(policy_statements)
)

scraping_layer = aws.lambda_.LayerVersion(
    "scraping_layer",
    layer_name="scraping_layer",
    code=pulumi.FileArchive("lambda_layer/requirements.zip"),
    compatible_runtimes=["python3.12"],
)

lambdas = {}
for subdir in scripts_subdirectories:
    scripts = [os.path.splitext(f)[0] for f in os.listdir(subdir) if f.endswith(".py")]
    for script in scripts:
        lambdas[script] = aws.lambda_.Function(
            script,
            name=script,
            role=lambda_role.arn,
            runtime=aws.lambda_.Runtime.PYTHON3D12,
            timeout=900,
            memory_size=1024,
            layers=[scraping_layer.arn, pandas_layer_arn],
            code=pulumi.FileArchive(subdir),
            handler=f"{script}.lambda_handler",
            environment={"variables": {"AWS_ACCOUNT_ID": AWS_ACCOUNT_ID}},
        )
