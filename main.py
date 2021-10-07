import configparser
import json
import yaml
import shutil 
import os
import uuid
from subprocess import check_output, Popen, call, PIPE, STDOUT

configFile = "./config/config.ini"
reproduceFolder = "./reproduce"
reproducePara = "reproduce_para.json"
reproduceConf = "reproduce_conf.json"


def readsummary(): 
    config = configparser.ConfigParser()
    config.read(configFile)
    return (str(config['summary']['cloud']),str(config['summary']['application']),str(config['summary']['your_key_path']),str(config['summary']['your_key_name']),str(config['summary']['your_git_username']),str(config['summary']['your_git_password']),str(config['summary']['git_link']),str(config['summary']['bootstrap']))

def readparameter():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (str(config['parameter']['experiment_docker']),str(config['parameter']['experiment_name']),str(config['parameter']['data']),str(config['parameter']['command']))

def readawscloud():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (int(config['cloud.aws']['instance_num']),str(config['cloud.aws']['SUBNET_ID']),str(config['cloud.aws']['INSTANCE_TYPE']),str(config['cloud.aws']['VPC_ID']))

def readazurecloud():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (str(config['cloud.azure']['REGION']),str(config['cloud.azure']['resourceGroupID']),str(config['cloud.azure']['resourceGroupName']),str(config['cloud.azure']['instance_num']),str(config['cloud.azure']['INSTANCE_TYPE']))

def readbill():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (float(config['bill']['vm_price']),float(config['bill']['bigdata_cluster_price']),float(config['bill']['network_price']),float(config['bill']['storage_price']),float(config['bill']['container_price']))

def readreprodeuce():
    config = configparser.ConfigParser() 
    config.read(configFile)
    return (str(config['reproduce']['reproduce_storage']),str(config['reproduce']['reproduce_database']))

cloud_provider, application, your_key_path, your_key_name, your_git_username, your_git_password, git_link, bootstrap = readsummary()  #str
vm_price, bigdata_cluster_price, network_price, storage_price, container_price = readbill()  #float
experiment_docker, experiment_name, data, command = readparameter()   #str
reproduce_storage, reproduce_database = readreprodeuce()
if cloud_provider == "aws":
    instance_num, SUBNET_ID, INSTANCE_TYPE, VPC_ID = readawscloud() #int,str
elif cloud_provider == "azure":
    REGION, resourceGroupID, resourceGroupName, instance_num, INSTANCE_TYPE = readazurecloud() #str


class Aws:
    def __init__(self, name):
        self.name = name
        self.app_path = "AwsServerlessTemplate/"+application+"/"     #bigdata_analytics/cpu_analytics/gpu_analytics

        #self.para_path = self.app_path+"parameter.json"
        self.depoly_conf_path = self.app_path+"depoly_config.json"

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

    def aws_depoly(self):
        #config
        with open(self.depoly_conf_path, "r") as json_file:
            depoly_conf_dict = json.load(json_file)
        depoly_new_conf_dict = depoly_conf_dict
        depoly_new_conf_dict = self.para_control(depoly_new_conf_dict,'InstanceType',INSTANCE_TYPE)
        depoly_new_conf_dict = self.para_control(depoly_new_conf_dict,'InstanceNum',instance_num)
        depoly_new_conf_dict = self.para_control(depoly_new_conf_dict,'Ec2KeyName',your_key_name)
        depoly_new_conf_dict = self.para_control(depoly_new_conf_dict,'Ec2KeyPath',your_key_path)
        depoly_new_conf_dict = self.para_control(depoly_new_conf_dict,'SubnetId',SUBNET_ID)
        depoly_new_conf_dict = self.para_control(depoly_new_conf_dict,'VpcId',VPC_ID)
        #TODO: generate security group resources for each test
        with open(reproduceFolder+"/"+reproduceConf, "w") as json_file:
            json.dump(depoly_conf_dict, json_file, indent=4)

        #lambda
        lambda_path = self.app_path+"lambda"
        target_path = reproduceFolder+"/lambda"
        shutil.copytree(lambda_path, target_path)
        return 'start depolying on aws'

class Azure:
    def __init__(self, name):
        self.name = name
        self.app_path = "AzureServerlessTemplate/"+application+"/"     #bigdata_analytics/cpu_analytics/gpu_analytics

        self.para_path = self.app_path+"parameter.json"
        self.depoly_conf_path = self.app_path+"depoly_config.json"
        self.command_path = self.app_path+"command_script.sh"
        self.lambda_path = self.app_path+"fake_lambda.sh"

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

    def azure_depoly(self):
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
        with open(self.depoly_conf_path, "r") as json_file:
            depoly_conf_dict = json.load(json_file)
        with open(reproduceFolder+"/"+reproduceConf, "w") as json_file:
            json.dump(depoly_conf_dict, json_file, indent=4)

        #command_script
        with open(self.command_path, "r") as bash_file:
            command_script = bash_file.readlines()
        with open(reproduceFolder+"/reproduce_command.sh", "w") as bash_file:
            bash_file.writelines(command_script)

        #fake_lambda
        with open(self.lambda_path, "r") as bash_file:
            lambda_script = bash_file.readlines()
        with open(reproduceFolder+"/reproduce_lambda.sh", "w") as bash_file:
            bash_file.writelines(lambda_script)

        #lambda
        lambda_path = self.app_path+"lambda"
        target_path = reproduceFolder+"/lambda"
        shutil.copytree(lambda_path, target_path)

        return 'start depolying on azure'

# class Provider:
#     def __init__(self, name):
#         self.name = name

#     def __str__(self):
#         return 'the {} provider'.format(self.name)

#     def provider_deploy(self):
#         return 'is depolying on provider'

class Adapter:
    def __init__(self, obj, adapted_methods):
        self.obj = obj
        self.__dict__.update(adapted_methods)    

    def __str__(self):     
        return str(self.obj)

def main():

    # objects = [Computer('Asus')]

    # synth = Synthesizer('moog')
    # objects.append(Adapter(synth, dict(execute=synth.play)))

    # human = Human('Bob')
    # objects.append(Adapter(human, dict(execute=human.speak)))

    # for i in objects:
    #     print('{} {}'.format(str(i), i.execute()))

    for files in os.listdir(reproduceFolder):
        path = os.path.join(reproduceFolder, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

    if cloud_provider == "aws":
        Cloud = Aws(application)
        template=Adapter(Cloud, dict(execute=Cloud.aws_depoly))
    elif cloud_provider == "azure":
        Cloud = Azure(application)
        template=Adapter(Cloud, dict(execute=Cloud.azure_depoly))
    else:
        raise SystemExit("NOT IMPLEMENTED CLOUD, currect support aws, azure")

    print('{} {}'.format(str(template), template.execute()))

    id_uuid = str(uuid.uuid4())
    if cloud_provider == "aws":
        call('cd '+reproduceFolder+' && sam validate -t '+reproduceConf, shell=True)
    #     call('cd '+reproduceFolder+' && sam build -t '+reproduceConf, shell=True)
    #     call('cd '+reproduceFolder+' && sam deploy --stack-name samautoanalytics --s3-bucket %s --s3-prefix %s --capabilities CAPABILITY_IAM --no-confirm-changeset --debug --force-upload'%(reproduce_storage,id_uuid), shell=True)
    # elif cloud_provider == "azure":
    #     call('cd '+reproduceFolder+' && az deployment group create --name Deploy LocalTemplate --resource-group %s --template-file %s --parameters %s --debug'%(resourceGroupName,reproduceConf,reproducePara), shell=True)
if __name__ == "__main__":
    main()
    