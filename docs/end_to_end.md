## End-to-end: one-click execution with RPAC

We put an example in our public S3 bucket `s3://reproduceexampleofrpac`.
The default `one_click` option in `main.py` file is False. If you would like to execution data analytics in one-click, change this option to True.

Follow previous steps to set up your configurations, then run `python3 main.py`. 

Example output:
```
-------------------------------------------------------------------------------------------------

Successfully created/updated stack - rpacautoanalytics in us-west-2

2021-12-13 15:59:24,551 | Sending Telemetry: {'metrics': [{'commandRun': {'requestId': '3c959d38-55c7-4e72-9498-bf5c3ba3921f', 'installationId': '30e2028a-1307-4162-b381-0bdaec1cfb5a', 'sessionId': 'c388d34c-c484-4ef8-ad39-79070198bfce', 'executionEnvironment': 'CLI', 'ci': False, 'pyversion': '3.7.10', 'samcliVersion': '1.24.1', 'awsProfileProvided': False, 'debugFlagProvided': True, 'region': '', 'commandName': 'sam deploy', 'duration': 174177, 'exitReason': 'success', 'exitCode': 0}}]}
2021-12-13 15:59:25,002 | HTTPSConnectionPool(host='aws-serverless-tools-telemetry.us-west-2.amazonaws.com', port=443): Read timed out. (read timeout=0.1)
Resource provisioning success. Logs folder s3://reproduceexampleofrpac/a7bc55a5-c214-4cd4-b2e8-53d50ecc1546.
{
    "FailedEntryCount": 0,
    "Entries": [
        {
            "EventId": "464243f0-f277-32a4-4d1e-b6693a27533a"
        }
    ]
}
Cloud execution start.

```

The outputs and execution history will be stored at DynamoDB and S3. The address are `reproduce_database` and `reproduce_storage` arguments that you provided in `./ConfigTemplate/resource.ini`.
