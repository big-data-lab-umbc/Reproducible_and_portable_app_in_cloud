import argparse
import boto.ec2
from boto.s3.connection import S3Connection
import sys, os
import time
from subprocess import check_output, Popen, call, PIPE, STDOUT
import fcntl
from threading import Thread
import platform
import configparser
import json
import uuid

from boto.s3.key import Key
import boto

configFile = "./config/config.ini"
emrConfigFile = "config/emr-configuration-ecr-public.json"
e_uuid = uuid.uuid4()

# s3_bucket_name = 'python-sdk-boto-{}'.format(int((time.time())))
s3_bucket_name = 'xintest'
storage = 's3'

def readsummary(): 
    config = configparser.ConfigParser()
    config.read(configFile)
    return (str(config['summary']['your_key_path']),str(config['summary']['your_key_name']),str(config['summary']['your_git_username']),str(config['summary']['your_git_password']),str(config['summary']['git_link']))

def readparameter():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (str(config['parameter']['experiment_name']),str(config['parameter']['driver_memory']))

def readaws():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (int(config['aws']['instance_num']),str(config['aws']['SUBNET_ID']),str(config['aws']['INSTANCE_TYPE']),str(config['aws']['REGION']),str(config['aws']['SECURITY_GROUP_ID']),str(config['aws']['VPC_ID']))

def readbill():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (float(config['bill']['EC2_price']),float(config['bill']['EMR_price']),float(config['bill']['VPC_price']),float(config['bill']['EBS_price']),float(config['bill']['data_size']))

your_key_path, your_key_name, your_git_username, your_git_password, git_link = readsummary()  #str
EC2_price, EMR_price, VPC_price, EBS_price, data_size = readbill()  #float
experiment_name, driver_memory = readparameter()   #str
instance_num, SUBNET_ID, INSTANCE_TYPE, REGION, SECURITY_GROUP_ID, VPC_ID = readaws() #int,str

if not boto.config.has_section('ec2'):
    boto.config.add_section('ec2')
    boto.config.setbool('ec2','use-sigv4',True)

secgroups = {
    REGION:SECURITY_GROUP_ID, 
}
regions = sorted(secgroups.keys())[::-1]
    
def get_ec2_instances_private_ip(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    if ec2_conn:
        result = []
        reservations = ec2_conn.get_all_reservations(filters={"instance.group-name": "ElasticMapReduce-master"})
        for reservation in reservations:
            if reservation:       
                for ins in reservation.instances:
                    if ins.public_dns_name: 
                        currentIP = ins.private_ip_address
                        print(currentIP)
                        result.append(currentIP)
                        
        return result
    else:
        print('Region failed', region)
        return None

def get_ec2_instances_ip(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    if ec2_conn:
        result = []
        reservations = ec2_conn.get_all_reservations(filters={"instance.group-name": "ElasticMapReduce-master"})
        for reservation in reservations:
            if reservation:       
                for ins in reservation.instances:
                    if ins.public_dns_name: 
                        currentIP = ins.public_dns_name.split('.')[0][4:].replace('-','.')
                        result.append(currentIP)
                        print(currentIP)
        return result
    else:
        print('Region failed', region)
        return None

def get_ec2_instances_id(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    if ec2_conn:
        result = []
        reservations = ec2_conn.get_all_reservations(filters={"instance.group-name": "ElasticMapReduce-master"})
        for reservation in reservations:    
            for ins in reservation.instances:
                print(ins.id)
                result.append(ins.id)
        return result
    else:
        print('Region failed', region)
        return None

def terminate_all_instances(region):
    ec2_conn = boto.ec2.connect_to_region(region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
    idList = []
    if ec2_conn:
        reservations = ec2_conn.get_all_reservations()
        for reservation in reservations:   
            if reservation:    
                for ins in reservation.instances:
                    idList.append(ins.id)
        ec2_conn.terminate_instances(instance_ids=idList)

def ipAll():
    result = []
    for region in regions:
        result += get_ec2_instances_ip(region) or []
    open('master_public_ip','w').write('\n'.join(result))
    return result

def privateIPAll():
    result = []
    for region in regions:
        result += get_ec2_instances_private_ip(region) or []
    open('master_private_ip','w').write('\n'.join(result))
    return result

def getIP():
    return [l for l in open('master_public_ip', 'r').read().split('\n') if l]

def idAll():
    result = []
    for region in regions:
        result += get_ec2_instances_id(region) or []
    return result

def join_get(l,sep):
    if isinstance(l,list):
        output = []
        for i in l:
            output.append('hadoop@'+i)
        return sep.join(output)
    if isinstance(l,str):
        return 'hadoop@'+l

def callFabFromIPList(l, work):
    print('fab -i %s -H %s %s' % (your_key_path, join_get(l,','), work))
    call('fab -i %s -H %s %s' % (your_key_path, join_get(l,','), work), shell=True)

c = callFabFromIPList

def testfab():
    c(getIP(), 'getAllIP')

def RunCausality():
    # create endpoint
    endpoint_start = time.time()
    call("echo '[%s] Start create endpoints.' | tee -a ./logs/%s"%(endpoint_start,e_uuid), shell=True)
    call('aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface \
        --vpc-id "%s" \
        --service-name com.amazonaws.%s.ecr.api \
        --security-group-ids "%s" \
        --subnet-ids "%s" > api_endpoint'%(VPC_ID,REGION,SECURITY_GROUP_ID,SUBNET_ID), shell=True)
    with open('api_endpoint') as f:
        api_endpoint_id = json.load(f)['VpcEndpoint']['VpcEndpointId']

    call('aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface \
        --vpc-id "%s" \
        --service-name com.amazonaws.%s.ecr.dkr \
        --security-group-ids "%s" \
        --subnet-ids "%s" > dkr_endpoint'%(VPC_ID,REGION,SECURITY_GROUP_ID,SUBNET_ID), shell=True)
    with open('dkr_endpoint') as ff:
        dkr_endpoint_id = json.load(ff)['VpcEndpoint']['VpcEndpointId']

    # create cluster
    emr_start = time.time()
    call("echo '[%s] Start create cluster.' | tee -a ./logs/%s"%(emr_start,e_uuid), shell=True)
    call('aws emr create-cluster \
        --name "EMR 6.0.0 with Docker" \
        --region %s \
        --release-label emr-6.0.0 \
        --applications Name=Hadoop Name=Spark \
        --use-default-roles \
        --ec2-attributes KeyName=%s,SubnetId=%s \
        --instance-type %s \
        --instance-count %s \
        --configuration file://%s | tee emr_cluster'%(REGION,your_key_name,SUBNET_ID,INSTANCE_TYPE,str(instance_num),emrConfigFile), shell=True)
    with open('emr_cluster') as fff:
        cluster_id = json.load(fff)['ClusterId']
    
    # check cluster status
    tmp = 0
    while 1:
        time.sleep(5)
        call('aws emr describe-cluster --cluster-id %s > emr_cluster_states'%cluster_id, shell=True)
        with open('emr_cluster_states') as ffff:
            target_cluster_status = json.load(ffff)['Cluster']['Status']['State']
        call('aws ec2 describe-vpc-endpoints --vpc-endpoint-ids %s > api_states'%api_endpoint_id, shell=True)
        with open('api_states') as api_f:
            api_status = json.load(api_f)['VpcEndpoints'][0]['State']
        call('aws ec2 describe-vpc-endpoints --vpc-endpoint-ids %s > dkr_states'%dkr_endpoint_id, shell=True)
        with open('dkr_states') as dkr_f:
            dkr_status = json.load(dkr_f)['VpcEndpoints'][0]['State']

        if api_status == "available" and dkr_status == "available" and tmp == 0:
            endpoints_end = time.time()
            call("echo '[%s] Create endpoints successfully.' | tee -a ./logs/%s"%(endpoints_end,e_uuid), shell=True)
            tmp = 1
        if target_cluster_status == "WAITING":
            cluster_end = time.time()
            call("echo '[%s] Create EMR cluster successfully.' | tee -a ./logs/%s"%(cluster_end,e_uuid), shell=True)
            break
    
    # setting hadoop
    result = []
    for region in regions:
        result += get_ec2_instances_ip(region) or []
    prepare_start = time.time()
    open('master_public_ip','w').write('\n'.join(result))
    call('echo "[%s] Start setting hadoop." | tee -a ./logs/%s'%(prepare_start,e_uuid), shell=True)
    c(getIP(), 'hadoopSetting')
    call('echo "[%s] Setting hadoop successfully." | tee -a ./logs/%s'%(time.time(),e_uuid), shell=True)

    # environment prepare
    call('echo "[%s] Start login cluster and pull causality-analytics application." | tee -a ./logs/%s'%(time.time(),e_uuid), shell=True)
    c(getIP(), 'prepare %s %s %s'%(your_git_username,your_git_password,git_link))
    prepare_end = time.time()
    call('echo "[%s] Prepare causality application successfully." | tee -a ./logs/%s'%(time.time(),e_uuid), shell=True)

    # start experiment
    call('echo "[%s] Start experiment." | tee -a ./logs/%s'%(time.time(),e_uuid), shell=True)
    c(getIP(), 'start %s %s'%(experiment_name,driver_memory))
    experiment_end = time.time()
    call('echo "[%s] End experiment." | tee -a ./logs/%s'%(experiment_end,e_uuid), shell=True)

    Cost = ((experiment_end-emr_start)/3600*EC2_price*(instance_num+1))\
        +(VPC_price*(experiment_end-endpoint_start)/3600)\
        +((experiment_end-emr_start)/3600*EMR_price*(instance_num+1))\
        +(data_size*EBS_price)
    call('echo "Experiment cost is %s." | tee -a ./logs/%s'%(str(Cost),e_uuid), shell=True)

    print("\nBudgetary cost = ",Cost,", Execution time = ",(experiment_end-endpoint_start)/3600)
    print("endpoint_init_time = ",(endpoints_end-endpoint_start)/3600,", emr_init_time = ",(cluster_end-emr_start)/3600,", prepare_time = ",(prepare_end-prepare_start)/3600,", experiment_time = ",(experiment_end-prepare_end)/3600)

def DeleteCluster():
    with open('api_endpoint') as f:
        api = json.load(f)
    with open('dkr_endpoint') as ff:
        dkr = json.load(ff)
    with open('emr_cluster') as fff:
        emr = json.load(fff)
    
    if storage == 's3':
        s3_conn = S3Connection(access_key,secret_key)
        bucket = s3_conn.get_bucket(s3_bucket_name)
        k = Key(bucket)
        k.key = 'config.ini'
        k.set_contents_from_filename(configFile,policy='private')  
    
    call('aws ec2 delete-vpc-endpoints --vpc-endpoint-ids %s %s'%(api['VpcEndpoint']['VpcEndpointId'],dkr['VpcEndpoint']['VpcEndpointId']), shell=True)
    call('aws emr terminate-clusters --cluster-ids %s'%emr['ClusterId'], shell=True)

def createCluster():
    if storage == 's3':
        s3_conn = S3Connection(access_key,secret_key)
        try:
            bucket = s3_conn.create_bucket(s3_bucket_name,location=REGION,policy='private')
        except:
            bucket = s3_conn.get_bucket(s3_bucket_name)

    api_command = 'aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface \
        --vpc-id "%s" \
        --service-name com.amazonaws.%s.ecr.api \
        --security-group-ids "%s" \
        --subnet-ids "%s"'%(VPC_ID,REGION,SECURITY_GROUP_ID,SUBNET_ID)
    call('%s > api_endpoint'%api_command, shell=True)
    if storage == 's3':
        k = Key(bucket)
        k.key = 'api_endpoint'
        k.set_contents_from_filename('api_endpoint')  
    with open('api_endpoint') as f:
        api_endpoint_id = json.load(f)['VpcEndpoint']['VpcEndpointId']

    dkr_command = 'aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface \
        --vpc-id "%s" \
        --service-name com.amazonaws.%s.ecr.dkr \
        --security-group-ids "%s" \
        --subnet-ids "%s"'%(VPC_ID,REGION,SECURITY_GROUP_ID,SUBNET_ID)
    call('%s > dkr_endpoint'%dkr_command, shell=True)
    if storage == 's3':
        k = Key(bucket)
        k.key = 'dkr_endpoint'
        k.set_contents_from_filename('dkr_endpoint') 
    with open('dkr_endpoint') as ff:
        dkr_endpoint_id = json.load(ff)['VpcEndpoint']['VpcEndpointId']

    # create cluster
    emr_command = 'aws emr create-cluster \
        --name "EMR 6.0.0 with Docker" \
        --region %s \
        --release-label emr-6.0.0 \
        --applications Name=Hadoop Name=Spark \
        --use-default-roles \
        --ec2-attributes KeyName=%s,SubnetId=%s \
        --instance-type %s \
        --instance-count %s \
        --configuration file://%s'%(REGION,your_key_name,SUBNET_ID,INSTANCE_TYPE,str(instance_num),emrConfigFile)
    call('%s | tee emr_cluster'%emr_command, shell=True)
    if storage == 's3':
        k = Key(bucket)
        k.key = 'emr_cluster'
        k.set_contents_from_filename('emr_cluster') 
    with open('emr_cluster') as fff:
        cluster_id = json.load(fff)['ClusterId']
    
    # check cluster status
    tmp = 0
    while 1:
        time.sleep(5)
        call('aws emr describe-cluster --cluster-id %s > emr_cluster_states'%cluster_id, shell=True)
        with open('emr_cluster_states') as ffff:
            target_cluster_status = json.load(ffff)['Cluster']['Status']['State']
        call('aws ec2 describe-vpc-endpoints --vpc-endpoint-ids %s > api_states'%api_endpoint_id, shell=True)
        with open('api_states') as api_f:
            api_status = json.load(api_f)['VpcEndpoints'][0]['State']
        call('aws ec2 describe-vpc-endpoints --vpc-endpoint-ids %s > dkr_states'%dkr_endpoint_id, shell=True)
        with open('dkr_states') as dkr_f:
            dkr_status = json.load(dkr_f)['VpcEndpoints'][0]['State']

        if api_status == "available" and dkr_status == "available" and tmp == 0:
            print("Create endpoints successfully.")
            if storage == 's3':
                k = Key(bucket)
                k.key = 'api_states'
                k.set_contents_from_filename('api_states')  #overwrite
                k.key = 'dkr_states'
                k.set_contents_from_filename('dkr_states')
            tmp = 1
        if target_cluster_status == "WAITING":
            print("Create EMR cluster successfully.")
            if storage == 's3':
                k = Key(bucket)
                k.key = 'emr_cluster_states'
                k.set_contents_from_filename('emr_cluster_states')  
                k.key = 'start_cluster.sh'
                k.set_contents_from_string('#!/bin/sh\nset -e\n\n%s\n%s\nsleep 3\n%s\n'%(api_command,dkr_command,emr_command))
            break


def s3create():
    s3_conn = S3Connection(access_key,secret_key)
    bucket = s3_conn.create_bucket(s3_bucket_name,location=REGION)

def hadoopSetting():
    result = []
    for region in regions:
        result += get_ec2_instances_ip(region) or []
    open('master_public_ip','w').write('\n'.join(result))
    c(getIP(), 'hadoopSetting')

def prepare():
    c(getIP(), 'prepare %s %s %s'%(your_git_username,your_git_password,git_link))

def start():    
    c(getIP(), 'start %s %s'%(experiment_name,driver_memory))

def getlog():
    c(getIP(), 'getlog')

def get_bill():
    call('aws ce get-cost-and-usage \
    --time-period Start=2021-04-01,End=2021-04-30 \
    --granularity DAILY \
    --metrics "UsageQuantity" "NormalizedUsageAmount" "AmortizedCost" "BlendedCost" "UnblendedCost"', shell=True)

if  __name__ =='__main__':
  try: __IPYTHON__
  except NameError:
    parser = argparse.ArgumentParser()
    parser.add_argument('access_key', help='Access Key')
    parser.add_argument('secret_key', help='Secret Key')
    args = parser.parse_args()
    access_key = args.access_key
    secret_key = args.secret_key

    import IPython
    IPython.embed()

