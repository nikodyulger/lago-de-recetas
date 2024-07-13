import os
import json
import pulumi_aws as aws

from utils import websites

params = {}
for web in websites:
    base_name = os.path.basename(web)
    init_data = json.load(
        open(f"../scraping/init_data/init_data_{base_name}.json", "r")
    )

    params[web] = aws.ssm.Parameter(
        f"init_data_{base_name}",
        name=f"/config/init_data_{base_name}",
        type=aws.ssm.ParameterType.STRING,
        value=json.dumps(init_data),
        overwrite=False,
    )
