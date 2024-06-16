import pulumi
import pulumi_aws as aws

import lambdas
import step_functions
import schedulers
import params

bucket = aws.s3.Bucket("raw_recipe_data_bucket", bucket="raw-recipe-data-bucket")


# Export the name of the bucket
pulumi.export("bucket_name", bucket.id)
