#!/bin/sh

set -e

automation_unique_name='DAtest5'    #TODO: should be a unique name

config_name='DAAutomation.yaml'   # CausalityAutomation.yaml/DAAutomation.yaml
stack_name='samautomation'
s3_bucket='aws-sam-cli-managed-default-samclisourcebucket-xscicpwnc0z3'
#config_file = 'samconfig.toml'

sam validate -t ./${config_name}
sam build -t ./${config_name}
sam deploy --stack-name ${stack_name} --s3-bucket ${s3_bucket} --s3-prefix ${automation_unique_name} --capabilities CAPABILITY_IAM --no-confirm-changeset --debug --force-upload

#aws s3 cp ./${config_file} s3://${s3_bucket}/${automation_unique_name}/