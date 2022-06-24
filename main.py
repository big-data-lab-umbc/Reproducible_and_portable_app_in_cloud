import configparser
import json
import yaml
import shutil 
import os
import uuid
import argparse
import glob
import time
from subprocess import check_output, Popen, call, PIPE, STDOUT

resconfigFile = "./ConfigTemplate/resource.ini"
appconfigFile = "./ConfigTemplate/application.ini"
personalconfigFile = "./ConfigTemplate/personal.ini"

reproduceFolder = "./reproduce"
reproducePara = "pipeline_para.json"
reproduceConf = "pipeline.json"
reproduceEvent = "my_event.json"

id_uuid = str(uuid.uuid4())

#cloud,your_key_path,your_key_name,your_python_runtime,your_git_username,your_git_password,cloud_credentials
def readsummary(): 
    config = configparser.ConfigParser()
    config.read(personalconfigFile)
    return (str(config['summary']['cloud']),str(config['summary']['your_key_path']),str(config['summary']['your_key_name']),str(config['summary']['your_git_username']),str(config['summary']['your_git_password']),str(config['summary']['your_python_runtime']),str(config['summary']['cloud_credentials']))

#experiment_docker,data_address,command,bootstrap
def readparameter():
    config = configparser.ConfigParser() 
    config.read(appconfigFile)
    return (str(config['parameter']['experiment_docker']),str(config['parameter']['data_address']),str(config['parameter']['command']),str(config['parameter']['bootstrap']))

def readbigdataengine():
    config = configparser.ConfigParser() 
    config.read(resconfigFile)
    return (str(config['bigdataengine']['application']))

def readawscloud():
    config = configparser.ConfigParser() 
    config.read(resconfigFile)
    return (str(config['cloud.aws']['REGION']),int(config['cloud.aws']['instance_num']),str(config['cloud.aws']['SUBNET_ID']),str(config['cloud.aws']['INSTANCE_TYPE']),str(config['cloud.aws']['VPC_ID']))

def readazurecloud():
    config = configparser.ConfigParser() 
    config.read(resconfigFile)
    return (str(config['cloud.azure']['REGION']),str(config['cloud.azure']['resourceGroupID']),str(config['cloud.azure']['resourceGroupName']),str(config['cloud.azure']['instance_num']),str(config['cloud.azure']['INSTANCE_TYPE']))

# def readbill():
#     config = configparser.ConfigParser() 
#     config.read(resconfigFile)
#     return (float(config['bill']['vm_price']),float(config['bill']['bigdata_cluster_price']),float(config['bill']['network_price']),float(config['bill']['storage_price']),float(config['bill']['container_price']))

def readreprodeuce():
    config = configparser.ConfigParser() 
    config.read(resconfigFile)
    return (str(config['reproduce']['reproduce_storage']),str(config['reproduce']['reproduce_database']))

cloud_provider, your_key_path, your_key_name, your_git_username, your_git_password, your_python_runtime, cloud_credentials = readsummary()  #str
# vm_price, bigdata_cluster_price, network_price, storage_price, container_price = readbill()  #float
experiment_docker, data_address, command, bootstrap = readparameter()   #str
application = readbigdataengine()
reproduce_storage, reproduce_database = readreprodeuce()

if cloud_credentials.split(":")[1]:
    cloud_access_key = cloud_credentials.split(":")[0]
    cloud_secret_key = cloud_credentials.split(":")[1]
else:
    print("Please provide the key-value pair of your cloud credentials. Format is <Access key ID:Secret key ID>. In order to find your credentials, see https://console.aws.amazon.com/iam/home?region=us-west-2#security_credential.")
    exit(0)

def contain_underscores(test_str):
    res = False
    for ele in test_str:
        if ele.isupper():
            res = True
            return res
    return res
if "_" in reproduce_storage or reproduce_storage[-1]=="-" or contain_underscores(reproduce_storage):
    print("The bucket names cannot contain underscores, uppercase letters, or ending with a hyphen. The detailed bucket naming rules can be find in https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html.")
    exit(0)
    
if cloud_provider == "aws":
    REGION, instance_num, SUBNET_ID, INSTANCE_TYPE, VPC_ID = readawscloud() #int,str
    
    call('aws configure set aws_access_key_id '+cloud_access_key, shell=True)
    call('aws configure set aws_secret_access_key '+cloud_secret_key, shell=True)
    output_stream = os.popen('aws ec2 describe-instance-type-offerings --filters Name=instance-type,Values=%s --region %s'%(INSTANCE_TYPE,REGION))
    output_json = json.load(output_stream)
    try:
        output_json['InstanceTypeOfferings'][0]['InstanceType']
    except:
        print("Your instance type is not valid in region %s."%REGION)
        exit(0)
    
    data_filename = data_address.split('/')[-1]
    data_bucketname = data_address.split('/')[-2]
elif cloud_provider == "azure":
    REGION, resourceGroupID, resourceGroupName, instance_num, INSTANCE_TYPE = readazurecloud() #str


class Aws:
    def __init__(self, name):
        self.name = name
        self.app_path = "AwsServerlessTemplate/"+application+"/"    

        #self.para_path = self.app_path+"parameter.json"
        self.deploy_conf_path = self.app_path+"deploy_config.json"
        self.deploy_event_path = self.app_path+"SampleEvent.json"
        self.deploy_lambda_path = self.app_path+"lambda"
        self.terminateCMD = ""

    def __str__(self):
        return '{} the aws template'.format(self.name)

    def para_control(self, para_dict, key, value):
        if value == "":
            pass
        else:
            try:
                para_dict['Parameters'][key]['Default'] = value
            except:
                pass
        return para_dict

    def event_control(self, event_dict, path, key, value):
        if value == "":
            pass
        else:
            try:
                event_dict['Configurations'][path][key] = value
            except:
                if path == 'ec2':
                    event_dict['Configurations'].update({'ec2': {"accessKey": value,"secretKey": ""}})
                if path == 'comm':
                    event_dict['Commands'][key] = value
                elif path == '':
                    event_dict['Configurations'][key] = value
        return event_dict

    def reproduce_args(self,args):
        self.app_path = './ExecutionHistory/%s/'%args.execution_history
        self.deploy_conf_path = glob.glob(self.app_path + "/*.template", recursive = True)[0]
        self.deploy_event_path = glob.glob(self.app_path + "/event.json", recursive = True)[0]
        self.deploy_lambda_path = glob.glob(self.app_path + "/*_FILES", recursive = True)[0]
        
    def terminate_when_finish(self):
        self.terminateCMD = "aws cloudformation delete-stack --stack-name rpacautoanalytics"

    def aws_deploy(self):
        #pipeline
        with open(self.deploy_conf_path, "r") as json_file:
            deploy_conf_dict = json.load(json_file)
        deploy_new_conf_dict = deploy_conf_dict
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'InstanceType',INSTANCE_TYPE)
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'InstanceNum',instance_num)
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'Ec2KeyName',your_key_name)
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'Ec2KeyPath',your_key_path)
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'SubnetId',SUBNET_ID)
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'VpcId',VPC_ID)
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'SimpleTableName',reproduce_database)
        deploy_new_conf_dict = self.para_control(deploy_new_conf_dict,'PythonRuntime',your_python_runtime)
        #TODO: generate security group resources for each test
        with open(reproduceFolder+"/"+reproduceConf, "w") as json_file:
            json.dump(deploy_conf_dict, json_file, indent=4)

        #event
        with open(self.deploy_event_path, "r") as json_file:
            event_dict = json.load(json_file)
        new_event_dict = event_dict
        new_event_dict = self.event_control(new_event_dict,'ec2','accessKey',cloud_access_key)
        new_event_dict = self.event_control(new_event_dict,'ec2','secretKey',cloud_secret_key)
        new_event_dict = self.event_control(new_event_dict,'output_result','bucketname',reproduce_storage)
        new_event_dict = self.event_control(new_event_dict,'output_result','prefix',id_uuid)
        new_event_dict = self.event_control(new_event_dict,'output_event','bucketname',reproduce_storage)
        new_event_dict = self.event_control(new_event_dict,'output_event','prefix',id_uuid)
        new_event_dict = self.event_control(new_event_dict,'source_data','bucketname',data_bucketname)
        new_event_dict = self.event_control(new_event_dict,'source_data','filename',data_filename)
        new_event_dict = self.event_control(new_event_dict,'','docker_image',experiment_docker)
        new_event_dict = self.event_control(new_event_dict,'','command_line',command)
        new_event_dict = self.event_control(new_event_dict,'','terminate',self.terminateCMD)
        new_event_dict = self.event_control(new_event_dict,'comm','bash',bootstrap)
        with open(reproduceFolder+"/"+reproduceEvent, "w") as json_file:
            json.dump(new_event_dict, json_file, indent=4)

        #lambda
        target_path = reproduceFolder+"/lambda"
        shutil.copytree(self.deploy_lambda_path, target_path)
        return 'start deploying on aws'

class Azure:
    def __init__(self, name):
        self.name = name
        self.app_path = "AzureServerlessTemplate/"+application+"/"     #SparkAnalytics/DaskAnalytics/HovorodAnalytics

        self.para_path = self.app_path+"parameter.json"
        self.deploy_conf_path = self.app_path+"deploy_config.json"
        self.command_path = self.app_path+"command_script.sh"
        self.lambda_path = self.app_path+"simu_lambda.sh"

    def __str__(self):
        return '{} the azure template'.format(self.name)

    def para_control(self, para_dict, key, value):
        if value == "":
            pass
        else:
            try:
                para_dict['parameters'][key]['value'] = value
            except:
                pass
        return para_dict

    def reproduce_args(self,args):
        pass

    def terminate_when_finish(self):
        pass

    def azure_deploy(self):
        #para
        with open(self.para_path, "r") as json_file:
            parameter_dict = json.load(json_file)
        parameter_new_dict = parameter_dict
        parameter_new_dict = self.para_control(parameter_new_dict,'instanceSize',INSTANCE_TYPE)
        parameter_new_dict = self.para_control(parameter_new_dict,'instanceCount',instance_num)
        #parameter_new_dict = self.para_control(parameter_new_dict,'customData',bootstrap)
        with open(reproduceFolder+"/"+reproducePara, "w") as json_file:
            json.dump(parameter_new_dict, json_file, indent=4)

        #config
        with open(self.deploy_conf_path, "r") as json_file:
            deploy_conf_dict = json.load(json_file)
        with open(reproduceFolder+"/"+reproduceConf, "w") as json_file:
            json.dump(deploy_conf_dict, json_file, indent=4)

        #command_script
        with open(self.command_path, "r") as bash_file:
            command_script = bash_file.readlines()
        with open(reproduceFolder+"/reproduce_command.sh", "w") as bash_file:
            bash_file.writelines(command_script)

        #simu_lambda
        with open(self.lambda_path, "r") as bash_file:
            lambda_script = bash_file.readlines()
        with open(reproduceFolder+"/reproduce_lambda.sh", "w") as bash_file:
            bash_file.writelines(lambda_script)

        #lambda
        lambda_path = self.app_path+"lambda"
        target_path = reproduceFolder+"/lambda"
        shutil.copytree(lambda_path, target_path)

        return 'start deploying on azure'

# class Provider:
#     def __init__(self, name):
#         self.name = name

#     def __str__(self):
#         return 'the {} provider'.format(self.name)

#     def provider_deploy(self):
#         return 'is deploying on provider'

class Adapter:
    def __init__(self, obj, adapted_methods):
        self.obj = obj
        self.__dict__.update(adapted_methods)    

    def __str__(self):     
        return str(self.obj)

def get_vmss_ip(resourceGroupName):
    call('az vmss list-instance-public-ips --resource-group %s --name RPAC | tee ./temp.json'%resourceGroupName, shell=True)
    with open("./temp.json", "r") as json_file:
        list_instance_public_ips = json.load(json_file)
    os.remove("./temp.json")

    vmss_ip = list_instance_public_ips[0]['ipAddress']
    print(vmss_ip)
    return vmss_ip #string

def main():

    parser = argparse.ArgumentParser(description='RPAC Toolkit.')
    parser.add_argument('--execution_history', type=str,
                        default="", help='Folder name of execution history to reproduce, or URI of execution history.')
    parser.add_argument('--one_click', action="store_true",
                        default=False, help="Allow one_click execution to be used by RPAC, implies '--one_click'. Note this argument will terminate all cloud resources after execution finished.")
    parser.add_argument('--terminate', action="store_true",
                        default=False, help="Terminate all cloud resources, implies '--terminate'.")
    args = parser.parse_args()

    if args.execution_history:
        if "s3://" in args.execution_history:
            try:
                history_folder = args.execution_history.split('/')[-1]
                call('aws s3 cp %s ./ExecutionHistory/%s --recursive'%(args.execution_history,history_folder), shell=True)
                for files in os.listdir('./ExecutionHistory/%s'%history_folder):
                    if "." not in files:
                        call('mkdir %s_FILES'%files, shell=True)
                        call('unzip ./ExecutionHistory/%s/%s -d ./ExecutionHistory/%s/%s_FILES/'%(history_folder,files,history_folder,files), shell=True)
                        os.remove("./ExecutionHistory/%s/%s"%(history_folder,files))
            except:
                print("Invalid S3 URI.")
                exit(0)
        elif not os.path.isdir('./ExecutionHistory/%s'%args.execution_history):
            print("Can't find execution history folder ./ExecutionHistory/%s"%args.execution_history)
            exit(0)
    
    if args.terminate:
        if cloud_provider == "aws":
            call('aws cloudformation delete-stack --stack-name rpacautoanalytics', shell=True)
        elif cloud_provider == "azure":
            call('az resource delete --name RPAC --resource-group %s --resource-type "Microsoft.Compute/virtualMachineScaleSets"'%resourceGroupName, shell=True)
            call('az network nsg delete --resource-group %s --name basicNsgStartlyResource-vnet-nic01'%resourceGroupName, shell=True)
        exit(0)

    for files in os.listdir(reproduceFolder):
        path = os.path.join(reproduceFolder, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

    if cloud_provider == "aws":
        Cloud = Aws(application)
        if args.execution_history:
            Cloud.reproduce_args(args)
        if args.one_click:
            Cloud.terminate_when_finish()
        template=Adapter(Cloud, dict(execute=Cloud.aws_deploy))
    elif cloud_provider == "azure":
        Cloud = Azure(application)
        if args.execution_history:
            Cloud.reproduce_args(args)
        if args.one_click:
            Cloud.terminate_when_finish()
        template=Adapter(Cloud, dict(execute=Cloud.azure_deploy))
    else:
        raise SystemExit("NOT IMPLEMENTED CLOUD, currect support aws, azure")

    print('{} {}'.format(str(template), template.execute()))

    if cloud_provider == "aws":
        #call('aws configure set aws_access_key_id '+cloud_access_key, shell=True)
        #call('aws configure set aws_secret_access_key '+cloud_secret_key, shell=True)

        call('cd '+reproduceFolder+' && sam validate -t '+reproduceConf, shell=True)
        call('cd '+reproduceFolder+' && sam build -t '+reproduceConf, shell=True)
        call('cd '+reproduceFolder+' && sam deploy --stack-name rpacautoanalytics --s3-bucket %s --s3-prefix %s --capabilities CAPABILITY_IAM --no-confirm-changeset --debug --force-upload --use-json'%(reproduce_storage,id_uuid), shell=True)
        print("Resource provisioning success. Logs folder s3://%s/%s."%(reproduce_storage,id_uuid))
        
        if args.one_click:
            with open(reproduceFolder+"/"+reproduceEvent, "r") as json_file:
                event_dict = json.load(json_file)
            event_detail = json.dumps(event_dict).replace('\"','\\"')
            call('aws events put-events --entries \'[{"Source": "custom.reproduce", "DetailType": "RPAC", "Detail": "%s"}]\''%event_detail, shell=True)
            print("Cloud execution start.")
    
    elif cloud_provider == "azure":
        call('az login', shell=True)
        # call('az login -u %s -p %s'%(cloud_access_key,cloud_secret_key), shell=True)

        call('cd '+reproduceFolder+' && az deployment group create --name DeployRPACPipeline --resource-group %s --template-file %s --parameters %s --debug'%(resourceGroupName,reproduceConf,reproducePara), shell=True)

        if args.one_click:
            ''' # TODO: perpare event for one_click asynchronized. (Now --one_click option is synchronized.)
            with open(reproduceFolder+"/"+reproduceEvent, "r") as json_file:
                event_dict = json.load(json_file)
            call('endpoint=$(az eventgrid topic show --name RPACEvent -g %s --query "endpoint" --output tsv)'%resourceGroupName, shell=True)
            call('eventgridkey=$(az eventgrid topic key list --name RPACEvent -g %s --query "key1" --output tsv)'%resourceGroupName, shell=True)
            call('curl -X POST -H "aeg-sas-key: $eventgridkey" -d "[{"id": "%s", "eventType": "custom.reproduce", "subject": "RPAC", "data":%s, "eventTime": "%s"}]" $endpoint'%(id_uuid,event_detail,time.time()), shell=True)
            '''

            time.sleep(10) # wait for VM's bootstrap
            call('export vmssIP=%s && export account_name=%s && export key=%s && bash ./reproduce/reproduce_lambda.sh'%(get_vmss_ip(resourceGroupName),cloud_access_key,cloud_secret_key), shell=True)

            call('az resource delete --name RPAC --resource-group %s --resource-type "Microsoft.Compute/virtualMachineScaleSets"'%resourceGroupName, shell=True)
            call('az network nsg delete --resource-group %s --name basicNsgStartlyResource-vnet-nic01'%resourceGroupName, shell=True)

if __name__ == "__main__":
    main()
