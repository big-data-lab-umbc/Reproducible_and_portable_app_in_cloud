#!/bin/sh
set -e

aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface         --vpc-id "vpc-81450cf9"         --service-name com.amazonaws.us-west-2.ecr.api         --security-group-ids "sg-058eb4f97ec6e76be"         --subnet-ids "subnet-5e38fc14"
aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface         --vpc-id "vpc-81450cf9"         --service-name com.amazonaws.us-west-2.ecr.dkr         --security-group-ids "sg-058eb4f97ec6e76be"         --subnet-ids "subnet-5e38fc14"
sleep 3
aws emr create-cluster         --name "EMR 6.0.0 with Docker"         --region us-west-2         --release-label emr-6.0.0         --applications Name=Hadoop Name=Spark         --use-default-roles         --ec2-attributes KeyName=id_rsa,SubnetId=subnet-5e38fc14         --instance-type c5.2xlarge         --instance-count 2         --configuration file://config/emr-configuration-ecr-public.json
