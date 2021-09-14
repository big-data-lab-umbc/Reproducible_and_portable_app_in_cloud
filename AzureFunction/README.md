## Deploy, Analysis, and Reproduce automatically on Azure (AzureFunction)

### Prerequisites:  
Install [VScodeExtention](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions) in VScode.

### Deploy and execute applications
1. Configuration

Use your customized configurations in each application dirctory. Also replace the AccountName and $AccountKey in <MyFunctionProj/local.settings.json>. 

2. Deploy applications
Azure provide multiple ways to deploy your serverless functions. Here we provide an uninteractive way using VScode based on [link](https://docs.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python). VScode provides one-click way for verification and deployment of your serverless functions.


3. Go to CloudFormation console, navigate to your application stack in [stacks](https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks). 
<p align="center"><img src="doc/cloudformation.png"/></p>

4. Navigate to your application AWS::Lambda::Function, and submit your config event <./SAMApplication/sample_event/your_event.json> to Lambda.
<p align="center"><img src="doc/lambda.png"/></p>

### Analysis applications
1. Navigate to DynamoDB AWS::Lambda::Function, and query your application outputs. Each record represents one execution of your application.
<p align="center"><img src="doc/dynamoDB.png"/></p>

### Reproduce applications
1. Each execution record includes all reproducibility configs. Use the reproducibility config as the <your_event.json> in Lambda, and submit for reproducibility.



set MyFunctionProJ as root dir. Use [VScodeExtention](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions) to deploy your Azure functions.

AccountName and $AccountKey in local.settings.json
