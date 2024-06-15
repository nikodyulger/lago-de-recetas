import os
import json
import pulumi_aws as aws
from pulumi import Output

from lambdas import lambdas

SCRAPING_DIRECTORY = "../scraping"
sfn_role = aws.iam.Role(
    "sfn_role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": f"states.{aws.config.region}.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
)

sfn_role_policy = aws.iam.RolePolicy(
    "sfn_role_policy",
    role=sfn_role.id,
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": "*",
                }
            ],
        }
    ),
)
subdirectories = filter(
    os.path.isdir,
    [
        os.path.join(SCRAPING_DIRECTORY, f)
        for f in os.listdir(SCRAPING_DIRECTORY)
        if f != "common"
    ],
)
step_functions = {}

for subdir in subdirectories:
    base_name = os.path.basename(subdir)
    init_lambda_arn = (
        lambdas[f"{base_name}_init"].arn
        if f"{base_name}_init" in lambdas.keys()
        else lambdas["common_init"].arn
    )
    crawler_lambda_arn = lambdas[f"{base_name}_crawler"].arn
    scraper_lambda_arn = lambdas[f"{base_name}_scraper"].arn
    step_functions[base_name] = aws.sfn.StateMachine(
        base_name,
        name=base_name,
        role_arn=sfn_role.arn,
        definition=Output.all(
            init_lambda_arn=init_lambda_arn,
            crawler_lambda_arn=crawler_lambda_arn,
            scraper_lambda_arn=scraper_lambda_arn,
        ).apply(
            lambda args: json.dumps(
                {
                    "Comment": f"Extracción y carga de datos de recetas de {base_name}",
                    "StartAt": "ReadInitData",
                    "States": {
                        "ReadInitData": {
                            "Type": "Task",
                            "Resource": args["init_lambda_arn"],
                            "OutputPath": "$.Payload",
                            "Parameters": {"Payload.$": "$"},
                            "Next": "Crawler",
                        },
                        "Crawler": {
                            "Type": "Task",
                            "Resource": args["crawler_lambda_arn"],
                            "OutputPath": "$.Payload",
                            "Parameters": {"Payload.$": "$"},
                            "Next": "Scrapper",
                        },
                        "Scrapper": {
                            "Type": "Task",
                            "Resource": args["scraper_lambda_arn"],
                            "OutputPath": "$.Payload",
                            "Parameters": {"Payload.$": "$"},
                            "End": True,
                        },
                    },
                }
            ),
        ),
    )
