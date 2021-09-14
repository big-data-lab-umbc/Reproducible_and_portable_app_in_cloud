#!/bin/bash

curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip awscliv2.zip && sudo ./aws/install
wget -P /home/azureuser/ https://causalityncerxyroxb2sg.blob.core.windows.net/data/5v_linear_1M.csv
git clone https://github.com/big-data-lab-umbc/ensemble_causality_learning.git

aws configure set aws_access_key_id <$your_access_key>
aws configure set aws_secret_access_key <$your_secret_key>
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/e0a3g4z6
sudo chmod 644 ~/.docker/config.json

hadoop fs -mkdir /user/azureuser
hadoop fs -put ~/.docker/config.json /user/azureuser/
hadoop fs -put ~/5v_linear_1M.csv

spark-submit --master yarn \
--deploy-mode cluster \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=public.ecr.aws/e0a3g4z6/causality-ensemble:latest \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG=hdfs:///user/azureuser/config.json \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=public.ecr.aws/e0a3g4z6/causality-ensemble:latest \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG=hdfs:///user/azureuser/config.json \
--conf spark.dynamicAllocation.enabled=True \
--driver-memory 8g \
--py-files ~/ensemble_causality_learning/sources.zip \
--files file:///home/azureuser/5v_linear_1M.csv \
~/ensemble_causality_learning/two_phase_algorithm_data.py 3 ~/5v_linear_1M.csv 100 3 -v
