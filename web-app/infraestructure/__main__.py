import json
import pulumi
import pulumi_aws as aws

config = pulumi.Config()
stack = pulumi.get_stack()
org = config.require("org")
stack_ref = pulumi.StackReference(f"{org}/notebooks-de-recetas/{stack}")


assume_role_policy = aws.iam.get_policy_document(
    statements=[
        {
            "actions": ["sts:AssumeRole"],
            "principals": [
                {
                    "identifiers": [
                        "build.apprunner.amazonaws.com",
                        "tasks.apprunner.amazonaws.com",
                    ],
                    "type": "Service",
                }
            ],
        }
    ]
)

policy_statements = stack_ref.get_output("endpoint_arn").apply(
    lambda arn: json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sagemaker:InvokeEndpoint",
                    ],
                    "Resource": f"{arn}",
                },
            ],
        }
    )
)


app_runner_execution_role = aws.iam.Role(
    "app_runner_execution_role",
    name="app_runner_execution_role",
    assume_role_policy=assume_role_policy.json,
    managed_policy_arns=[
        aws.iam.ManagedPolicy.AWS_APP_RUNNER_SERVICE_POLICY_FOR_ECR_ACCESS,
        aws.iam.ManagedPolicy.AMAZON_S3_READ_ONLY_ACCESS,
    ],
)

app_runner_role_policy = aws.iam.RolePolicy(
    "app_runner_role_policy",
    name="sagemake_endpoint_invocation",
    role=app_runner_execution_role.id,
    policy=policy_statements,
)

web_app_image = aws.ecr.Repository(
    "web_app_image",
    name="web_app_image",
    image_scanning_configuration={
        "scanOnPush": True,
    },
)


pulumi.export("web_app_image_url", web_app_image.repository_url)
