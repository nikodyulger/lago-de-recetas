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
    name="sagemaker_execution_role",
    assume_role_policy=assume_role_policy.json,
    managed_policy_arns=[aws.iam.ManagedPolicy.AMAZON_SAGE_MAKER_FULL_ACCESS],
)

notebooks_recetas = aws.sagemaker.NotebookInstance(
    "notebooks_recetas",
    name="notebooks-recetas",
    role_arn=sagemaker_execution_role.arn,
    instance_type="ml.t3.medium",
)

custom_model_image = aws.ecr.Repository(
    "custom_model_image",
    name="custom_model_image",
    image_scanning_configuration={
        "scanOnPush": True,
    },
)

custom_model = aws.sagemaker.Model(
    "custom_model",
    name="custom-model",
    execution_role_arn=sagemaker_execution_role.arn,
    primary_container={
        "image": custom_model_image.repository_url.apply(lambda arn: f"{arn}:latest"),
        "modelDataUrl": pulumi.Output.concat(
            "s3://", bucket.id, "/models/model.tar.gz"
        ),
    },
)

custom_model_endpoint_config = aws.sagemaker.EndpointConfiguration(
    "custom_model_endpoint_config",
    name="custom-model-endpoint-config",
    production_variants=[
        {
            "variantName": "dev",
            "modelName": custom_model.name,
            "serverlessConfig": {
                "maxConcurrency": 3,
                "memorySizeInMb": 1024,
                "provisionedConcurrency": 1,
            },
        }
    ],
)

endpoint = aws.sagemaker.Endpoint(
    "custom_model_endpoint",
    name="custom-model-endpoint",
    endpoint_config_name=custom_model_endpoint_config.name,
)

pulumi.export("bucket_name", bucket.id)
pulumi.export("notebook_instance_name", notebooks_recetas.name)
pulumi.export("notebook_instance_arn", notebooks_recetas.arn)
pulumi.export("custom_model_image_url", custom_model_image.repository_url)
pulumi.export("custom_model_name", custom_model.name)
pulumi.export("endpoint_name", endpoint.name)
pulumi.export("endpoint_arn", endpoint.arn)
