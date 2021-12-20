import logging
import json
import azure.functions as func

import asyncio
import os

from azure.common.credentials import (ServicePrincipalCredentials, get_azure_cli_credentials)
from msrestazure.azure_active_directory import MSIAuthentication
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential

from azure.mgmt.compute import compute_management_client
from azure.common.credentials import ServicePrincipalCredentials

# def main(myblob: func.InputStream, doc: func.Out[func.Document]):
#     logging.info(f"Python blob trigger function processed blob \n"
#                  f"Name: {myblob.name}\n"
#                  f"Blob Size: {myblob.length} bytes")
    
#     json_data = myblob.read()
#     logging.info(f"{json_data}")

#     try:
#         # Store output data using Cosmos DB output binding
#         doc.set(func.Document.from_json(json_data))
#         logging.info(f"Export success.")
#     except Exception as e:
#         logging.info(f"Error: {e}")
#         raise e



# def main(event: func.EventGridEvent, outputblob: func.Out[str]):

#     result = json.dumps({
#         'id': event.id,
#         'data': event.get_json(),
#         'topic': event.topic,
#         'subject': event.subject,
#         'event_type': event.event_type,
#     })

#     logging.info('Python EventGrid trigger processed an event: %s', result)

#     try:
#         outputblob.set(result)
#         logging.info(f"Export success.")
#     except Exception as e:
#         logging.info(f"Error: {e}")
#         raise e

def process_rg_instance(group):
    """
    Get the relevant pieces of information from a ResourceGroup instance.
    """
    return {
        "Name": group.name,
        "Id": group.id,
        "Location": group.location,
        "Tags": group.tags,
        "Properties": group.properties.provisioning_state if group.properties and group.properties.provisioning_state else None
    }

def vm_run_command(client,vm_name,commands):
    run_command_parameters = {
        'command_id': 'RunShellScript', 
        'script': [
            '%s'%commands           #'ls /tmp'
        ]
    }
    poller = client.virtual_machines.run_command(
            "StartlyResource",
            vm_name,
            run_command_parameters
    )
    result = poller.result()  # Blocking till executed
    print(result.value[0].message)  # stdout/stderr

async def list_rgs(credentials, subscription_id):
    """
    Get list of resource groups for the subscription id passed.
    """
    list_of_resource_groups = []

    with ResourceManagementClient(credentials, subscription_id) as rg_client:
        try:
            for i in rg_client.resource_groups.list():
                list_of_resource_groups.append(process_rg_instance(i))

        except Exception as e:
            logging.error("encountered: {0}".format(str(e)))

    return json.dumps(list_of_resource_groups)

async def main(event: func.EventGridEvent):

    if "MSI_ENDPOINT" in os.environ:
        credentials = MSIAuthentication()
    else:
        credentials, *_ = get_azure_cli_credentials()

    subscription_id = os.environ.get(
        'AZURE_SUBSCRIPTION_ID', '11111111-1111-1111-1111-111111111111')
    client = compute_management_client(credentials, subscription_id)

    print("@@@@@@@@@@ is ",credentials,"############ is ",DefaultAzureCredential())
    list_of_rgs = await list_rgs(credentials, subscription_id)

    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger processed an event: %s', result)

    vm_run_command(client,vm_name,"git clone")
