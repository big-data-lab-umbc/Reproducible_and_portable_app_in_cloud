#!/bin/sh

set -e

git clone https://github.com/big-data-lab-umbc/ensemble_causality_learning.git

hadoop fs -put ~/.docker/config.json /user/hadoop/
hadoop fs -put ~/5v_linear_10M.csv
spark-submit --master yarn \
--deploy-mode cluster \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=public.ecr.aws/e0a3g4z6/causality-ensemble \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG=hdfs:///user/hadoop/config.json \
--conf spark.executorEnv.YARN_CONTAINER_RUNTIME_DOCKER_MOUNTS=/etc/passwd:/etc/passwd:ro \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_TYPE=docker \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_IMAGE=public.ecr.aws/e0a3g4z6/causality-ensemble \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_CLIENT_CONFIG=hdfs:///user/hadoop/config.json \
--conf spark.yarn.appMasterEnv.YARN_CONTAINER_RUNTIME_DOCKER_MOUNTS=/etc/passwd:/etc/passwd:ro \
--conf spark.dynamicAllocation.enabled=True \
--driver-memory 5g \
--py-files ~/ensemble_causality_learning/sources.zip \
--files file:///home/hadoop/5v_linear_10M.csv \
~/ensemble_causality_learning/two_phase_algorithm_data.py 3 ~/5v_linear_10M.csv 240 3 -v
