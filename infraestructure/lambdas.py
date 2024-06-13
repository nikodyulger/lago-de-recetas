import json
import pulumi
import pulumi_aws as aws


lambda_role = aws.iam.Role('lambda_role',
                           assume_role_policy=json.dumps({
                               "Version": "2012-10-17",
                               "Statement": [
                                    {
                                        "Action": "sts:AssumeRole",
                                        "Principal": {
                                            "Service": "lambda.amazonaws.com"
                                        },
                                        "Effect": "Allow",
                                        "Sid": ""
                                    }
                                ]
                           })
)

lambda_role_policy = aws.iam.RolePolicy('lambda_role_policy',
                                        role=lambda_role.id,
                                        policy=json.dumps({
                                            "Version": "2012-10-17",
                                            "Statement": [{
                                                "Effect": "Allow",
                                                "Action": [
                                                    "logs:CreateLogGroup",
                                                    "logs:CreateLogStream",
                                                    "logs:PutLogEvents"
                                                ],
                                                "Resource": "arn:aws:logs:*:*:*"
                                            }]
                                        })
)

antena3_crawler = aws.lambda_.Function("antena3_crawler",
                                   role=lambda_role.arn,
                                   runtime=aws.lambda_.Runtime.PYTHON3D12,
                                   code=pulumi.AssetArchive({
                                       ".": pulumi.FileArchive("../scraping/antena3"),
                                   }),
                                   handler="antena3_crawler.lambda_handler",
                                   )
