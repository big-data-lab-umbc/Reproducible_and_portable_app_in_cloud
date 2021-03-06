#!/bin/sh

set -e

curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'
unzip awscliv2.zip
sudo ./aws/install

aws configure set aws_access_key_id xxxxxx
aws configure set aws_secret_access_key xxxxxx
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/e0a3g4z6
sudo chmod 644 ~/.docker/config.json

wget -O azcopy_v10.tar.gz https://aka.ms/downloadazcopy-v10-linux && tar -xf azcopy_v10.tar.gz --strip-components=1
./azcopy copy 'https://causalityncerxyroxb2sg.blob.core.windows.net/data/5v_linear_1M.csv' './'


git clone https://github.com/xxxxxx/ensemble_causality_learning.git

hadoop fs -mkdir /user/sshuser
hadoop fs -put ~/.docker/config.json /user/sshuser/
hadoop fs -put ~/5v_linear_1M.csv

spark-submit --master yarn \
--deploy-mode cluster \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=public.ecr.aws/e0a3g4z6/causality-ensemble:latest \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG=hdfs:///user/sshuser/config.json \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=public.ecr.aws/e0a3g4z6/causality-ensemble:latest \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG=hdfs:///user/sshuser/config.json \
--conf spark.dynamicAllocation.enabled=True \
--driver-memory 8g \
--py-files ~/ensemble_causality_learning/sources.zip \
--files wasbs:///user/sshuser/5v_linear_1M.csv \
~/ensemble_causality_learning/two_phase_algorithm_data.py 3 ~/5v_linear_1M.csv 100 3 -v