import json
import boto3
import os

ssm_client = boto3.client('ssm')
stepfunctions_client = boto3.client('stepfunctions')
eventbridge_client = boto3.client('events')


def lambda_handler(event, context):

    init_param_name = event.get("init_param_name")
    page_slice = os.getenv('page_slice')
    eb_rule_name = os.getenv('eb_rule_name')

    response = ssm_client.get_parameter(
        Name=init_param_name
    )

    init_data = json.loads(response['Parameter']['Value']) # dict with a list property { "pages": [...]}
    
    # Check if the list is not empty
    if len(init_data['pages']) > 0:

        pages = init_data['pages'][:page_slice]
        del init_data['pages'][:page_slice]
        
        print(f"Updated {init_param_name}")
        print(json.dumps(init_data, indent=4))
        
        # Update Parameter
        ssm_client.put_parameter(
            Name=init_param_name,
            Value=json.dumps(init_data),
            Overwrite=True
        )
    else:
        # disable the eventbridge rule
        eventbridge_client.disable_rule(
            Name=eb_rule_name
        )
        print(f"Rule '{eb_rule_name}' has been disabled successfully.")

    return {
        "pages": pages
    }