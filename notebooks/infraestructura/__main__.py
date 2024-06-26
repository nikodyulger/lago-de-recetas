import pulumi
from pulumi_aws import s3

bucket = s3.Bucket(
    "recipes_data_models_sagemaker_bucket",
    bucket="recipes-data-models-sagemaker-bucket",
)


pulumi.export("bucket_name", bucket.id)
