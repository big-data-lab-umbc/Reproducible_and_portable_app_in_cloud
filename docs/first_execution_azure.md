## First execution: get first execution in Azure Cloud

We use CloudRetrievalViaDask application in Azure as the example.

1. Fill in three configuration files in ./ConfigTemplate folder. 

> Note: For personal.ini, `cloud_credentials` is formated in `storage_account_name:storage_account_key`. 

2. Run `python3 main.py --one_click` to start RPAC for CloudRetrievalViaDask application.

> Note: Now `--one_click` option in Azure only supports synchronized operation. Every execution steps in RPAC will be printed out, until execution finish and resources termination.

3. The outputs and execution history will be stored at CosmosDB and Blob (Container) Storage once execution done. Users are able to scan and query execution history in [Data Explorer](https://portal.azure.com/#@umbc.onmicrosoft.com/resource/subscriptions/250c38e9-47a3-4d89-bc68-54155a7fe08e/resourcegroups/StartlyResource/providers/Microsoft.DocumentDB/databaseAccounts/causalityresult/dataExplorer) of Azure CosmosDB.

<p align="center"><img src="./figures/cosmosdb.png"/></p>

4. If you did not use `--one_click` option when RPAC launching, remember to terminate all resource by RPAC using `python3 main.py --ternimate`.
