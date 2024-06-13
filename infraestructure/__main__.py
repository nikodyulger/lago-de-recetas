import pulumi
import pulumi_aws as aws
import lambdas

bucket = aws.s3.Bucket('raw_recipe_data_bucket',
                   bucket="raw-recipe-data-bucket")


# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)
