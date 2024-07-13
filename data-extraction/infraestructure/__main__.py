import pulumi
import pulumi_aws as aws

import lambdas
import step_functions
import schedulers
import params

raw_bucket = aws.s3.Bucket("raw_recipe_data_bucket", bucket="raw-recipe-data-bucket")
pulumi.export("raw_bucket_name", raw_bucket.id)
