import logging

import azure.functions as func
# import boto3
# import json


#def main(req: func.HttpRequest) -> func.HttpResponse:
def main(req: func.HttpRequest, context: func.Context) -> str:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')

    logging.info(f'$$$ {context.function_name,context.invocation_id}')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')
            body = req_body.get('body')

    if name:
        logging.info(f'### {body}')
        # key = "azure"
        # # Write to DynamoDB.
        # table = boto3.resource('dynamodb',region_name="us-west-2",aws_access_key_id="AKIASHT77BI5S2QHPAPZ",aws_secret_access_key="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").Table(table_name)
        
        # item={'id':key, 'Results':body}
        # table.put_item(Item=item)
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
