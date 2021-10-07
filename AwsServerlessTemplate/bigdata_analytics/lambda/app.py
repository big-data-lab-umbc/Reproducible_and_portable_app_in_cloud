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
print('Loading function')

def get_ec2_instances_id(region,access_key,secret_key):
    ec2_conn = boto3.resource('ec2',region_name=region,aws_access_key_id=access_key,aws_secret_access_key=secret_key)
    
    if ec2_conn:
        for instance in ec2_conn.instances.all():
            if instance.state['Name'] == 'running' and instance.security_groups[0]['GroupName'] == 'ElasticMapReduce-master':
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
    return "aws s3 cp /home/ubuntu/%s s3://%s"%(filename,path)

def s3_object_version(bucketname,s3prefix):
    return "aws s3api list-object-versions --bucket %s --prefix %s --output text --query 'Versions[?IsLatest].[VersionId]'"%(bucketname,s3prefix)

def s3_get_object(bucketname,s3prefix,localpath,version):
    return "aws s3api get-object --bucket %s --key %s %s --version-id %s"%(bucketname,s3prefix,localpath,version)

def lambda1_handler(event, context):
    #pprint.pprint(dict(os.environ), width = 1)

    credentials = [event['Configurations']['awsRegion'],event['Configurations']['ec2']['accessKey'],event['Configurations']['ec2']['secretKey']]
    event['Configurations'].pop('ec2')
    masterInstanceId = get_ec2_instances_id(credentials[0],credentials[1],credentials[2])
    ssm_client = boto3.client('ssm',region_name=credentials[0],aws_access_key_id=credentials[1],aws_secret_access_key=credentials[2])

    start = time.time()
    send_command_to_master(masterInstanceId,\
        event['Commands']['gitClone'],\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        s3_get_object(event['Configurations']['source_data']["bucketname"],event['Configurations']['source_data']["prefix"],"/home/hadoop/"+event['Configurations']['source_data']["filename"],event['Configurations']['source_data']["version"]),\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        "mv /home/hadoop/"+event['Configurations']['source_data']["filename"]+" /home/hadoop/ensemble_causality_learning/",\
        ssm_client)
    # send_command_to_master(masterInstanceId,\
    #     "wget -P /home/hadoop/ https://kddworkshop.s3.us-west-2.amazonaws.com/5v_linear_9.5M.csv && mv /home/hadoop/5v_linear_9.5M.csv /home/hadoop/ensemble_causality_learning/",\
    #     ssm_client)


    send_command_to_master(masterInstanceId,\
        "hadoop fs -put /home/hadoop/.docker/config.json /user/hadoop/",\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        "hadoop fs -put /home/hadoop/ensemble_causality_learning/"+event['Configurations']['source_data']["filename"],\
        ssm_client)
    print('Setup success, start causality...')

    try:
        send_command_to_master(masterInstanceId,event['Configurations']['command_line'],ssm_client)
        print('Success')
    except Exception as e:
        print('Spark went wrong, please check spark logs.')
        raise e

    exe_time = (time.time()-start)/3600
    
    # copy ensemble_result from VM to S3
    send_command_to_master(masterInstanceId,\
        s3_put_object(event['Configurations']['output_result']["filename"],event['Configurations']['output_result']['bucketname']+"/"+event['Configurations']['output_result']['prefix']),\
        ssm_client)
    result_version = s3_object_version(event['Configurations']['output_result']["bucketname"],event['Configurations']['output_result']["prefix"])

    # copy ensemble_event from VM to S3
    send_command_to_master(masterInstanceId,\
        "echo "+json.dumps(event).replace("\"","\\'")+" | tee -a /home/ubuntu/"+event['Configurations']['output_event']["filename"],\
        ssm_client)
    send_command_to_master(masterInstanceId,\
        s3_put_object(event['Configurations']['output_event']["filename"],event['Configurations']['output_event']['bucketname']+"/"+event['Configurations']['output_event']['prefix']),\
        ssm_client)
    event_version = s3_object_version(event['Configurations']['output_event']["bucketname"],event['Configurations']['output_event']["prefix"])

    # caculate cost
    cost = (exe_time*event['Configurations']['bill']['EC2_price']*event['Configurations']['instance_num'])\
        +(event['Configurations']['bill']['VPC_price']*exe_time)\
        +(exe_time*event['Configurations']['bill']['EMR_price']*event['Configurations']['instance_num'])\
        +(event['Configurations']['bill']['data_size']*event['Configurations']['bill']['EBS_price'])
    
    print("Execution time = ",exe_time)
    print("Cost = ",cost)

    # send dynamoDB export info to s3 target bucket (only json on s3 target bucket can be exported to dynamoDB)
    record_json = generate_record(event['Configurations']['command_line'],\
        str(cost),\
        str(exe_time),\
        str(exe_time*cost),\
        "s3://"+event['Configurations']['source_data']["bucketname"]+"/"+event['Configurations']['source_data']["prefix"],\
        event['Configurations']['source_data']["version"],\
        "s3://"+event['Configurations']['output_ensemble_result']["bucketname"]+"/"+event['Configurations']['output_ensemble_result']["prefix"],\
        str(result_version),\
        "s3://"+event['Configurations']['output_ensemble_event']["bucketname"]+"/"+event['Configurations']['output_ensemble_event']["prefix"],\
        str(event_version))
    send_command_to_master(masterInstanceId,\
        "echo "+record_json+" | tee -a /home/hadoop/temp.json",\
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

def generate_record(command_line,Budgetary_cost,Execution_time,Performance_price_ratio,source_data,source_data_verion,ensemble_result,ensemble_result_version,reproducibility_config,reproducibility_config_version):
    record_dict = {'command_line':command_line, \
        'budgetary_cost':Budgetary_cost, 'execution_time':Execution_time, 'performance_price_ratio':Performance_price_ratio, \
        'source_data':source_data, 'source_data_verion':source_data_verion, \
        'program_result':ensemble_result, 'program_result_version':ensemble_result_version, \
        'reproducibility_config':reproducibility_config, 'reproducibility_config_version':reproducibility_config_version}
    replacetemp = json.dumps(record_dict)
    result = replacetemp.replace('"','\\"')
    return result