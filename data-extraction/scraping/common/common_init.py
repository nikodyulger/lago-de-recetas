import json
import boto3
import os

AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")
AWS_REGION = os.getenv("AWS_REGION")

ssm_client = boto3.client("ssm")
stepfunctions_client = boto3.client("stepfunctions")
scheduler_client = boto3.client("scheduler")


def lambda_handler(event, context):

    init_param_name = event.get("init_param_name")
    page_slice = event.get("page_slice")
    eb_rule_name = event.get("eb_rule_name")
    print(event)

    response = ssm_client.get_parameter(Name=init_param_name)

    init_data = json.loads(
        response["Parameter"]["Value"]
    )  # list of dicts { "category": "..", "pages": []}
    print(init_data)

    # Check if the list is not empty
    if len(init_data) > 0:

        category = init_data[0]["category"]
        pages = init_data[0]["pages"][:page_slice]
        del init_data[0]["pages"][:page_slice]

        if len(init_data[0]["pages"]) == 0:
            init_data = init_data[1:]

        print(f"Updated {init_param_name}")
        print(json.dumps(init_data, indent=4))

        # Update Parameter
        ssm_client.put_parameter(
            Name=init_param_name, Value=json.dumps(init_data), Overwrite=True
        )
    else:
        # disable the scheduler rule
        scheduler_client.update_schedule(
            Name=eb_rule_name,
            State="DISABLED",
            FlexibleTimeWindow={"Mode": "OFF"},
            ScheduleExpression="rate(15 minutes)",
            Target={
                "Arn": f"arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:common_init",
                "RoleArn": f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/event_rule_role",
            },
        )
        category, pages = None, None
        print(f"Rule '{eb_rule_name}' has been disabled successfully.")

    return {"category": category, "pages": pages}
