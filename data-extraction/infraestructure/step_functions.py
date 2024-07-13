import os
import json
import pulumi_aws as aws
import pulumi

from lambdas import lambdas
from utils import websites

sfn_role = aws.iam.Role(
    "sfn_role",
    name="sfn_role",
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

step_functions = {}

for web in websites:
    base_name = os.path.basename(web)
    init_lambda_arn = (
        lambdas[f"{base_name}_init"].arn
        if f"{base_name}_init" in lambdas.keys()
        else lambdas["common_init"].arn
    )
    crawler_lambda_arn = lambdas[f"{base_name}_crawler"].arn
    scraper_lambda_arn = lambdas[f"{base_name}_scraper"].arn

    sfn_name = f"scraper_{base_name}"
    step_functions[base_name] = aws.sfn.StateMachine(
        sfn_name,
        name=sfn_name,
        role_arn=sfn_role.arn,
        definition=pulumi.Output.all(
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
                            "InputPath": "$",
                            "OutputPath": "$",
                            "Next": "Crawler",
                        },
                        "Crawler": {
                            "Type": "Task",
                            "Resource": args["crawler_lambda_arn"],
                            "InputPath": "$",
                            "OutputPath": "$",
                            "Next": "Scrapper",
                        },
                        "Scrapper": {
                            "Type": "Task",
                            "Resource": args["scraper_lambda_arn"],
                            "InputPath": "$",
                            "OutputPath": "$",
                            "End": True,
                        },
                    },
                }
            ),
        ),
    )
