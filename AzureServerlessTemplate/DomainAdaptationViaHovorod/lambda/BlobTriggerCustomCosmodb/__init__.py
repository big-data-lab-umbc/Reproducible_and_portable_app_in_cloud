import logging
import datetime
import time
import json

import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client

def main(myblob: func.InputStream, doc: func.Out[func.Document]):
    # logging.info(f"Python blob trigger function processed blob \n"
    #              f"Name: {myblob.name}\n"
    #              f"Blob Size: {myblob.length} bytes")
    
    # json_data = myblob.read()
    # logging.info(f"{json_data}")

    # try:
    #     # Store output data using Cosmos DB output binding
    #     doc.set(func.Document.from_json(json_data))
    #     logging.info(f"Export success.")
    # except Exception as e:
    #     logging.info(f"Error: {e}")
    #     raise e

    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    json_data = myblob.read()
    logging.info(f"{json_data}")

    json_dict = json.loads(json_data)
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
    json_dict['id'] = timestamp
    json_dict_temp = json_dict
    json_dict['blob_records'] = str(json_dict_temp)

    # Obtain HOST and MASTER_KEY from: https://portal.azure.com/#@[user_email]/resource/subscriptions/[subscription_id]/resourceGroups/[resource_group_name]/providers/Microsoft.DocumentDb/databaseAccounts/[db_account_name]/keys
    HOST = "https://causalityresult.documents.azure.com:443/"
    MASTER_KEY = "xxxxxx"

    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    database_link = 'SampleDB/' + 'causality'
    #collection_link = database_link + '/colls/' + 'causality'
    try:
        document = json_dict
        client.CreateItem(database_link, document)
    except Exception as e:
        logging.info(f"Error: {e}")
        raise e
