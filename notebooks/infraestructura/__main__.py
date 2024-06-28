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

notebooks_recetas = aws.sagemaker.NotebookInstance(
    "notebooks_recetas",
    name="notebooks-recetas",
    role_arn=sagemaker_execution_role.arn,
    instance_type="ml.t3.medium",
)

pulumi.export("bucket_name", bucket.id)
pulumi.export("notebook_instance_name", notebooks_recetas.name)
pulumi.export("notebook_instance_arn", notebooks_recetas.arn)
