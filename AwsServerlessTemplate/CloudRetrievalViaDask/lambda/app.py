from __future__ import print_function
import boto3
import json
import urllib
import time
import sys
import os
import datetime
import pprint

s3_client = boto3.client('s3')
s3 = boto3.resource('s3')
print('Loading function')

def get_ec2_instances_id(region,access_key,secret_key):
    ec2_conn = boto3.resource('ec2',region_name=region,aws_access_key_id=access_key,aws_secret_access_key=secret_key)
    
    if ec2_conn:
        for instance in ec2_conn.instances.all():
            if instance.state['Name'] == 'running' and instance.security_groups[0]['GroupName'] == 'distributed_dl_starly':
                masterInstanceId = instance.instance_id
                print("Master Instance Id is ",masterInstanceId)
        return masterInstanceId
    else:
        print('Region failed', region)
        return None

def send_command_to_master(InstanceId,command,ssm_client):
    print("Ssm run command: ",command)
    response = ssm_client.send_command(InstanceIds=[InstanceId],DocumentName="AWS-RunShellScript",Parameters={'commands': [command]})

    command_id = response['Command']['CommandId']
    waiter = ssm_client.get_waiter("command_executed")

    while True:
        try:
            waiter.wait(CommandId=command_id,InstanceId=InstanceId)
            break
        except:
            print("SSM in progress")
            time.sleep(5)

    output = ssm_client.get_command_invocation(CommandId=command_id,InstanceId=InstanceId)
    if output['Status'] == 'Success':
        print('SSM success')
    else:
        print('SSM failed')

def s3_put_object(filename,path):
    return "aws s3 cp /home/ubuntu/%s s3://%s"%(filename,path) #aws s3 cp /home/ubuntu/result.txt s3://aws-sam-cli-managed-default-samclisourcebucket-xscicpwnc0z3/26d1eef0-6875-42eb-b987-689213e25c66/result.txt

def s3_object_version(bucketname,s3prefix):
    return "aws s3api list-object-versions --bucket %s --prefix %s --output text --query 'Versions[?IsLatest].[VersionId]'"%(bucketname,s3prefix)

def s3_get_latest_version(bucketname,s3prefix):
    versions = s3.Bucket(bucketname).object_versions.filter(Prefix=s3prefix)
    for version in versions:
        obj = version.get()
        return obj.get('VersionId')
        break

def s3_get_object(bucketname,s3prefix,localpath,version):
    return "aws s3api get-object --bucket %s --key %s %s --version-id %s"%(bucketname,s3prefix,localpath,version)

def lambda1_handler(event, context):
    #pprint.pprint(dict(os.environ), width = 1)
    print("###########",event["detail"])
    event = event["detail"]

    credentials = [event['Configurations']['awsRegion'],event['Configurations']['ec2']['accessKey'],event['Configurations']['ec2']['secretKey']]
    event['Configurations'].pop('ec2')
    masterInstanceId = get_ec2_instances_id(credentials[0],credentials[1],credentials[2])
    ssm_client = boto3.client('ssm',region_name=credentials[0],aws_access_key_id=credentials[1],aws_secret_access_key=credentials[2])

    start = time.time()
    send_command_to_master(masterInstanceId,\
        "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh",\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        "sudo service docker start && sudo usermod -a -G docker ubuntu && sudo chmod 666 /var/run/docker.sock && sudo apt install unzip",\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        "docker pull "+event['Configurations']['docker_image'],\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        event['Commands']['gitClone'],\
        ssm_client)

    send_command_to_master(masterInstanceId,\
        "unzip /home/ubuntu/"+event['Configurations']['source_data']["filename"]+" -d /home/ubuntu/",\
        ssm_client)
    print('Setup success, start domain adaptation...')

    try:
        if "`" in event['Configurations']['command_line']:
            real_command = event['Configurations']['command_line'].replace("`","'")
            send_command_to_master(masterInstanceId,\
                real_command+" | tee -a /home/ubuntu/"+event['Configurations']['output_result']["filename"],\
                ssm_client)
        else:
            send_command_to_master(masterInstanceId,\
                event['Configurations']['command_line']+" | tee -a /home/ubuntu/"+event['Configurations']['output_result']["filename"],\
                ssm_client)
        print('Program success')
    except Exception as e:
        print('CR went wrong, please check logs.')
        raise e

    exe_time = (time.time()-start)/3600
    
    # copy result from VM to S3
    send_command_to_master(masterInstanceId,\
    'curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install',\
    ssm_client)
    send_command_to_master(masterInstanceId,\
        s3_put_object(event['Configurations']['output_result']["filename"],event['Configurations']['output_result']['bucketname']+"/"+event['Configurations']['output_result']['prefix']+"/"+event['Configurations']['output_result']['filename']),\
        ssm_client)
    result_version = s3_get_latest_version(event['Configurations']['output_result']["bucketname"],event['Configurations']['output_result']["prefix"]+"/"+event['Configurations']['output_result']['filename'])

    # copy event from VM to S3
    send_command_to_master(masterInstanceId,\
        "echo "+json.dumps(event).replace("\"","\\'")+" | tee -a /home/ubuntu/"+event['Configurations']['output_event']["filename"],\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        s3_put_object(event['Configurations']['output_event']["filename"],event['Configurations']['output_event']['bucketname']+"/"+event['Configurations']['output_event']['prefix']+"/"+event['Configurations']['output_event']['filename']),\
        ssm_client)
    event_version = s3_get_latest_version(event['Configurations']['output_event']["bucketname"],event['Configurations']['output_event']["prefix"]+"/"+event['Configurations']['output_event']['filename'])

    # caculate cost
    cost = (exe_time*event['Configurations']['bill']['EC2_price']*event['Configurations']['instance_num'])\
        +(event['Configurations']['instance_num']*event['Configurations']['bill']['EBS_price'])\
        +(event['Configurations']['bill']['data_size'])
    
    print("Execution time = ",exe_time)
    print("Cost = ",cost)

    # send dynamoDB export info to s3 target bucket <os.environ['S3_LOGBucketNAME']>
    # (only json on s3 target bucket can be exported to dynamoDB)
    record_json = generate_record(event['Configurations']['command_line'],\
        str(cost),\
        str(exe_time),\
        str(exe_time*cost),\
        "s3://"+event['Configurations']['source_data']["bucketname"]+"/"+event['Configurations']['source_data']["prefix"]+"/"+event['Configurations']['output_result']['filename'],\
        event['Configurations']['source_data']["version"],\
        "s3://"+event['Configurations']['output_result']["bucketname"]+"/"+event['Configurations']['output_result']["prefix"]+"/"+event['Configurations']['output_result']['filename'],\
        str(result_version),\
        "s3://"+event['Configurations']['output_event']["bucketname"]+"/"+event['Configurations']['output_event']["prefix"]+"/"+event['Configurations']['output_event']['filename'],\
        str(event_version))
    send_command_to_master(masterInstanceId,\
        "echo "+record_json+" | tee -a /home/ubuntu/temp.json",\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        s3_put_object("temp.json",os.environ['S3_LOGBucketNAME']+"/temp.json"),\
        ssm_client)


def lambda2_handler(event, context):
    
    table_name = os.environ['TABLE_NAME']
    print("Connect from dynamodb to s3...")

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    try:
        s3_ob = s3_client.get_object(Bucket=bucket, Key=key)
        json_dict = json.loads(s3_ob['Body'].read())
        
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

        table = boto3.resource('dynamodb').Table(table_name)
        
        #item={'id':key, 'DateTime':timestamp, 'Status':json_dict, 'Command Line':command_line, 'Budgetary_cost':Budgetary_cost, 'Execution_time':Execution_time, 'Performance_price_ratio':Performance_price_ratio, 'source_data':source_data, 'ensemble_result':ensemble_result, 'reproducibility_config':reproducibility_config}
        #table.put_item(Item=item)
        json_dict['id'] = timestamp
        json_dict_temp = json_dict
        json_dict['s3_records'] = str(json_dict_temp)
        table.put_item(Item=json_dict)

        s3_client.delete_object(Bucket=bucket, Key=key)
        return 'Success'
    except Exception as e:
        print("Error processing object {} from bucket {}. Event {}".format(key, bucket, json.dumps(event, indent=2)))
        raise e

def generate_record(command_line,Budgetary_cost,Execution_time,Performance_price_ratio,source_data,source_data_verion,program_result,program_result_version,reproducibility_config,reproducibility_config_version):
    record_dict = {'command_line':command_line, \
        'budgetary_cost':Budgetary_cost, 'execution_time':Execution_time, 'performance_price_ratio':Performance_price_ratio, \
        'source_data':source_data, 'source_data_verion':source_data_verion, \
        'program_result':program_result, 'program_result_version':program_result_version, \
        'reproducibility_config':reproducibility_config, 'reproducibility_config_version':reproducibility_config_version}
    replacetemp = json.dumps(record_dict)
    result = replacetemp.replace('"','\\"')
    try:
        result = result.replace('`','\`\'')
    return result