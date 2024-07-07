import json
import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx

config = pulumi.Config()
stack = pulumi.get_stack()
org = config.require("org")
stack_ref = pulumi.StackReference(f"{org}/notebooks-de-recetas/{stack}")

vpc = awsx.ec2.DefaultVpc("default-vpc")

web_security_group = aws.ec2.SecurityGroup(
    "web_security_group",
    name="web_security_group",
    egress=[
        {"fromPort": 0, "toPort": 0, "protocol": "-1", "cidrBlocks": ["0.0.0.0/0"]}
    ],
    ingress=[
        {
            "fromPort": 8501,
            "toPort": 8501,
            "protocol": "tcp",
            "cidrBlocks": ["0.0.0.0/0"],
        }
    ],
)

web_app_image = aws.ecr.Repository(
    "web_app_image",
    name="web_app_image",
    image_scanning_configuration={
        "scanOnPush": True,
    },
)

assume_role_policy = aws.iam.get_policy_document(
    statements=[
        {
            "actions": ["sts:AssumeRole"],
            "principals": [
                {
                    "identifiers": [
                        "ecs-tasks.amazonaws.com",
                    ],
                    "type": "Service",
                }
            ],
        }
    ]
)


policy_statements = stack_ref.get_output("endpoint_arn").apply(
    lambda arn: json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "sagemaker:InvokeEndpoint",
                    ],
                    "Resource": f"{arn}",
                },
            ],
        }
    )
)


task_execution_role = aws.iam.Role(
    "task_execution_role",
    name="task_execution_role",
    assume_role_policy=assume_role_policy.json,
    managed_policy_arns=[
        aws.iam.ManagedPolicy.AMAZON_ECS_TASK_EXECUTION_ROLE_POLICY,
        aws.iam.ManagedPolicy.AMAZON_S3_READ_ONLY_ACCESS,
    ],
)

task_execution_role_policy = aws.iam.RolePolicy(
    "task_execution_role_policy",
    name="sagemake_endpoint_invocation",
    role=task_execution_role.id,
    policy=policy_statements,
)


default_cluster = aws.ecs.Cluster("default_cluster", name="default")

web_app_service = aws.ecs.TaskDefinition(
    "web_app_service",
    family="web_app_service",
    task_role_arn=task_execution_role.arn,
    execution_role_arn=task_execution_role.arn,
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    cpu="512",
    memory="1024",
    container_definitions=web_app_image.repository_url.apply(
        lambda url: json.dumps(
            [
                {
                    "name": "streamlit",
                    "image": f"{url}:latest",
                    "cpu": 512,
                    "memory": 1024,
                    "essential": True,
                    "portMappings": [
                        {
                            "containerPort": 8501,
                            "hostPort": 8501,
                        }
                    ],
                }
            ]
        )
    ),
)

web_app_service = aws.ecs.Service(
    "web_app_service",
    cluster=default_cluster.arn,
    desired_count=0,  # 1
    launch_type="FARGATE",
    name="web_app_service",
    network_configuration={
        "subnets": vpc.public_subnet_ids,
        "assignPublicIp": True,
        "securityGroups": [web_security_group.id],
    },
    task_definition=web_app_service.arn,
)

pulumi.export("web_app_image_url", web_app_image.repository_url)
pulumi.export("vpcId", vpc.vpc_id)
pulumi.export("publicSubnetIds", vpc.public_subnet_ids)
