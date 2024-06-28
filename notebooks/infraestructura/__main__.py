import json
import pulumi
import pulumi_aws as aws

bucket = aws.s3.Bucket(
    "recipes_data_models_sagemaker_bucket",
    bucket="recipes-data-models-sagemaker-bucket",
)

assume_role_policy = aws.iam.get_policy_document(
    statements=[
        {
            "actions": ["sts:AssumeRole"],
            "principals": [
                {
                    "identifiers": ["sagemaker.amazonaws.com"],
                    "type": "Service",
                }
            ],
        }
    ]
)

sagemaker_execution_role = aws.iam.Role(
    "sagemaker_execution_role",
    assume_role_policy=assume_role_policy.json,
    managed_policy_arns=[aws.iam.ManagedPolicy.AMAZON_SAGE_MAKER_FULL_ACCESS],
)

pulumi.export("bucket_name", bucket.id)
