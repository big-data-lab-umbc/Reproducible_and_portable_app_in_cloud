import configparser
import json
import yaml
import shutil 
import os
import uuid
from subprocess import check_output, Popen, call, PIPE, STDOUT

resconfigFile = "./ConfigTemplate/resource.ini"
appconfigFile = "./ConfigTemplate/application.ini"
personalconfigFile = "./ConfigTemplate/personal.ini"

reproduceFolder = "./reproduce"
reproducePara = "pipeline_para.json"
reproduceConf = "pipeline.json"
reproduceEvent = "my_event.json"

id_uuid = str(uuid.uuid4())


def readsummary(): 
    config = configparser.ConfigParser()
    config.read(personalconfigFile)
    return (str(config['summary']['cloud']),str(config['summary']['application']),str(config['summary']['your_key_path']),str(config['summary']['your_key_name']),str(config['summary']['your_git_username']),str(config['summary']['your_git_password']),str(config['summary']['cloud_credentials']))

def readparameter():
    config = configparser.ConfigParser() 
    config.read(appconfigFile)
    return (str(config['parameter']['experiment_docker']),str(config['parameter']['experiment_name']),str(config['parameter']['data']),str(config['parameter']['command']),str(config['parameter']['git_link']),str(config['parameter']['bootstrap']))

def readawscloud():
    config = configparser.ConfigParser() 
    config.read(resconfigFile)
    return (int(config['cloud.aws']['instance_num']),str(config['cloud.aws']['SUBNET_ID']),str(config['cloud.aws']['INSTANCE_TYPE']),str(config['cloud.aws']['VPC_ID']))

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

cloud_provider, application, your_key_path, your_key_name, your_git_username, your_git_password, cloud_credentials = readsummary()  #str
# vm_price, bigdata_cluster_price, network_price, storage_price, container_price = readbill()  #float
experiment_docker, experiment_name, data, command, git_link, bootstrap = readparameter()   #str
reproduce_storage, reproduce_database = readreprodeuce()
if cloud_provider == "aws":
    instance_num, SUBNET_ID, INSTANCE_TYPE, VPC_ID = readawscloud() #int,str
    cloud_access_key = cloud_credentials.split(":")[0]
    cloud_secret_key = cloud_credentials.split(":")[1]
elif cloud_provider == "azure":
    REGION, resourceGroupID, resourceGroupName, instance_num, INSTANCE_TYPE = readazurecloud() #str


class Aws:
    def __init__(self, name):
        self.name = name
        self.app_path = "AwsServerlessTemplate/"+application+"/"     #SparkAnalytics/DaskAnalytics/HovorodAnalytics

        #self.para_path = self.app_path+"parameter.json"
        self.deploy_conf_path = self.app_path+"deploy_config.json"
        self.deploy_event_path = self.app_path+"SampleEvent.json"

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
                pass
        return event_dict

    def aws_deploy(self):
        #config
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
        #TODO: generate security group resources for each test
        with open(reproduceFolder+"/"+reproduceConf, "w") as json_file:
            json.dump(deploy_conf_dict, json_file, indent=4)

        with open(self.deploy_event_path, "r") as json_file:
            event_dict = json.load(json_file)
        new_event_dict = event_dict
        new_event_dict = self.event_control(new_event_dict,'ec2','accessKey',cloud_access_key)
        new_event_dict = self.event_control(new_event_dict,'ec2','secretKey',cloud_secret_key)
        new_event_dict = self.event_control(new_event_dict,'output_result','bucketname',reproduce_storage)
        new_event_dict = self.event_control(new_event_dict,'output_result','prefix',id_uuid)
        new_event_dict = self.event_control(new_event_dict,'output_event','bucketname',reproduce_storage)
        new_event_dict = self.event_control(new_event_dict,'output_event','prefix',id_uuid)
        with open(reproduceFolder+"/"+reproduceEvent, "w") as json_file:
            json.dump(new_event_dict, json_file, indent=4)

        #lambda
        lambda_path = self.app_path+"lambda"
        target_path = reproduceFolder+"/lambda"
        shutil.copytree(lambda_path, target_path)
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

    def azure_deploy(self):
        #para
        with open(self.para_path, "r") as json_file:
            parameter_dict = json.load(json_file)
        parameter_new_dict = parameter_dict
        parameter_new_dict = self.para_control(parameter_new_dict,'instanceSize',INSTANCE_TYPE)
        parameter_new_dict = self.para_control(parameter_new_dict,'instanceCount',instance_num)
        parameter_new_dict = self.para_control(parameter_new_dict,'customData',bootstrap)
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

def main():

    execution_history = False
    one_click = False

    # if len(sys.argv[1:]) >= 1:
    #     execution_history = sys.argv[1]

    for files in os.listdir(reproduceFolder):
        path = os.path.join(reproduceFolder, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

    if cloud_provider == "aws":
        Cloud = Aws(application)
        template=Adapter(Cloud, dict(execute=Cloud.aws_deploy))
    elif cloud_provider == "azure":
        Cloud = Azure(application)
        template=Adapter(Cloud, dict(execute=Cloud.azure_deploy))
    else:
        raise SystemExit("NOT IMPLEMENTED CLOUD, currect support aws, azure")

    print('{} {}'.format(str(template), template.execute()))

    if cloud_provider == "aws":
        call('aws configure set aws_access_key_id '+cloud_access_key, shell=True)
        call('aws configure set aws_secret_access_key '+cloud_secret_key, shell=True)

        call('cd '+reproduceFolder+' && sam validate -t '+reproduceConf, shell=True)
        call('cd '+reproduceFolder+' && sam build -t '+reproduceConf, shell=True)
        call('cd '+reproduceFolder+' && sam deploy --stack-name rpacautoanalytics --s3-bucket %s --s3-prefix %s --capabilities CAPABILITY_IAM --no-confirm-changeset --debug --force-upload'%(reproduce_storage,id_uuid), shell=True)
        print("Resource provisioning success. Logs folder s3://%s/%s."%(reproduce_storage,id_uuid))
        
        if one_click:
            with open(reproduceFolder+"/"+reproduceEvent, "r") as json_file:
                event_dict = json.load(json_file)
            event_detail = json.dumps(event_dict).replace('\"','\\"')
            call('aws events put-events --entries \'[{"Source": "custom.reproduce", "DetailType": "RPAC", "Detail": "%s"}]\''%event_detail, shell=True)
            print("Cloud execution start.")
    
    elif cloud_provider == "azure":
        call('az login', shell=True)

        call('cd '+reproduceFolder+' && az deployment group create --name Deploy LocalTemplate --resource-group %s --template-file %s --parameters %s --debug'%(resourceGroupName,reproduceConf,reproducePara), shell=True)


if __name__ == "__main__":
    main()
