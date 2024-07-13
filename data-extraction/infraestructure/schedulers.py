import os
import json
import pulumi
import pulumi_aws as aws

from datetime import datetime, timezone, timedelta

from step_functions import step_functions
from utils import websites

AWS_ACCOUNT_ID = aws.get_caller_identity().account_id
AWS_REGION = aws.get_region()
PAGE_SLICE = 5

event_rule_role = aws.iam.Role(
    "event_rule_role",
    name="event_rule_role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {"Service": "scheduler.amazonaws.com"},
                    "Effect": "Allow",
                }
            ],
        }
    ),
)

policy_statements = pulumi.Output.all(
    [sfn.arn for _, sfn in step_functions.items()]
).apply(
    lambda args: json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["states:StartExecution"],
                    "Resource": args.pop(),
                }
            ],
        }
    )
)

eb_rule_role_policy = aws.iam.RolePolicy(
    "eb_rule_role_policy", role=event_rule_role.id, policy=policy_statements
)

event_rules = {}
start_date = datetime.now(timezone.utc)
end_date = datetime.now(timezone.utc) + timedelta(7)
for web in websites:
    base_name = os.path.basename(web)
    event_rule_name = f"schedule_rule_{base_name}"
    event_rules[base_name] = aws.scheduler.Schedule(
        event_rule_name,
        name=event_rule_name,
        flexible_time_window=aws.scheduler.ScheduleFlexibleTimeWindowArgs(
            mode="OFF",
        ),
        start_date=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_date=end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        schedule_expression="rate(15 minutes)",
        target=aws.scheduler.ScheduleTargetArgs(
            arn=step_functions[base_name].arn.apply(lambda arn: f"{arn}"),
            role_arn=event_rule_role.arn,
            input=json.dumps(
                {
                    "init_param_name": f"/config/init_data_{base_name}",
                    "page_slice": PAGE_SLICE,
                    "eb_rule_name": event_rule_name,
                }
            ),
        ),
    )
