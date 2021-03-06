## First execution: get first execution with understanding and using RPAC toolkit

When RPAC toolkit is being utilized the first time, there is no execution history for querying and reproducing. Users need to prepare configurations to generate the pipeline file for the whole execution.

We use CloudRetrievalViaDask application in AWS Cloud without one_click as the tutorial example. Azure tutorial is also provided [here](./first_execution_azure.md).

Preparation: If you do not have a docker image yet, you can run commands like the following examples to create docker image from a docker file under the folder where Dockerfile is located and push it to [docker hub](https://hub.docker.com).
```
docker build -t jianwuwang/satellite-collocation:latest ./
docker push jianwuwang/satellite-collocation:latest
```


1. Fill in three configuration files in ./ConfigTemplate folder.


> Note: For personal.ini, `cloud_credentials` is formated in `credential_access_key:credential_secert_key`. For resource.ini, `reproduce_database` in DynamoDB and `reproduce_storage` in S3 need to be created with your aws account before starting RPAC.


2. Run `python3 main.py` to start RPAC for CloudRetrievalViaDask application. With user-provided configurations, a pipeline will be generated in `./reproduce` folder.

Example output:
```
-------------------------------------------------------------------------------------------------

Successfully created/updated stack - samautoanalytics in us-west-2

2021-11-29 13:32:45,098 | Sending Telemetry: {'metrics': [{'commandRun': {'requestId': 'e3fe2748-2818-46c5-84d2-b445f5e30ea3', 'installationId': '30e2028a-1307-4162-b381-0bdaec1cfb5a', 'sessionId': 'b145d6ba-98a7-4a13-80fc-ca3ce0251d43', 'executionEnvironment': 'CLI', 'ci': False, 'pyversion': '3.7.10', 'samcliVersion': '1.24.1', 'awsProfileProvided': False, 'debugFlagProvided': True, 'region': '', 'commandName': 'sam deploy', 'duration': 101240, 'exitReason': 'success', 'exitCode': 0}}]}

```

> Note: For the tutorial, we separate cloud provisioning with analytics execution (default `one_click = False` in [main.py](https://github.com/big-data-lab-umbc/Reproducible_and_portable_app_in_cloud/blob/b8aed7794df935ccdf9a5a193312955a1eab7e53/main.py#L19)). This step will only finish software and hardware provisioning of analytics automatically.


3. Send the [analytics execution event](../AwsServerlessTemplate/CloudRetrievalViaDask/SampleEvent.json) via [Amazon EventBridge](https://us-west-2.console.aws.amazon.com/events/home?region=us-west-2#/eventbuses). Set 'Event source' to `custom.reproduce` and copy the generated `./reproduce/my_event.json` to 'Event detail' box. Then scroll down the page and select `send` botton.

<p align="center"><img src="./figures/eventbridge.png"/></p>
<p align="center"><img src="./figures/sendevent.png"/></p>


4. The outputs and execution history will be stored at DynamoDB and S3 once execution done. The addresses are `reproduce_database` and `reproduce_storage` arguments that you provided in `./ConfigTemplate/resource.ini`. Users are able to scan and query execution history in [AWS Dynamodb](https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#item-explorer).

<p align="center"><img src="./figures/dynamodbscan.png"/></p>

5. Terminate RPAC. Delete the stack just created in [https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2](https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2). You can also use `python3 main.py --ternimate` for resources ternimation.
