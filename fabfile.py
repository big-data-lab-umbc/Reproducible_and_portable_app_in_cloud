from __future__ import with_statement
from fabric import *
from invoke import task, Exit
from fabric import Connection
import time, sys, os#, scanf
from io import BytesIO
import math
from fabric import ThreadingGroup as Group


@task
def host_type(conn):
    conn.run('uname -s')

@task
def gettime(conn):
    conn.run('date +%s.%N')
   

@task
def ping(conn):
    conn.run('ping -c 5 google.com')
    conn.run('echo "synced transactions set"')
    conn.run('ping -c 100 google.com')

@task
def getAllIP(conn):
    conn.run('hostname -I')
    
@task
def addhoc(conn):
    conn.sudo("for x in $(yarn application -list -appStates ACCEPTED | awk 'NR > 2 { print $1 }'); do yarn application -kill $x; done")
    conn.sudo("for x in $(yarn application -list -appStates RUNNING | awk 'NR > 2 { print $1 }'); do yarn application -kill $x; done")

@task
def hadoopSetting(conn):
    conn.sudo('yum update -y')
    conn.sudo('yum install -y git')
    conn.sudo('amazon-linux-extras install docker -y')
    conn.sudo('service docker start')
    conn.sudo('usermod -a -G docker hadoop')

    conn.run('curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"')
    conn.run('unzip awscliv2.zip')
    conn.sudo('./aws/install')

@task
def prepare(conn,username,password,git_link):
    conn.run('aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/e0a3g4z6')

    conn.sudo('chmod 644 ~/.docker/config.json')
    conn.run('hadoop fs -put ~/.docker/config.json /user/hadoop/')

    try:
        conn.sudo('rm -rf ensemble_causality_learning')
    except:
        pass
    conn.run('git clone %s'%git_link)
    # conn.run('git clone https://%s:%s@github.com/big-data-lab-umbc/causality-analytics.git'%(username, password))     # for private repository
    with conn.cd('ensemble_causality_learning'):
        # conn.run('wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate /"https://drive.google.com/uc?export=download&id=1SL-FoJ3thBxcKeFF97St1Rm2QmzYG6sR/" -O- | sed -rn "s/.*confirm=([0-9A-Za-z_]+).*/\1\n/p")&id=1SL-FoJ3thBxcKeFF97St1Rm2QmzYG6sR" -O 5v_linear_10M.csv && rm -rf /tmp/cookies.txt')
        # conn.run('hadoop fs -put 5v_linear_10M.csv')
        conn.run('curl -L https://umbc.box.com/shared/static/dq7ongvg3gpkieq7xd5n0n6zmv5xwfjm.csv --output 5v_nonlinear_50M.csv')
        conn.run('hadoop fs -put 5v_nonlinear_50M.csv')

@task
def start(conn, experiment_name, driver_memory):
    with conn.cd('ensemble_causality_learning'):
        conn.run('spark-submit --master yarn \
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
            --driver-memory %s \
            --py-files sources.zip \
            --files file:////home/hadoop/ensemble_causality_learning/5v_nonlinear_50M.csv \
            two_phase_algorithm_data.py 3 5v_nonlinear_50M.csv 240 3 -v'%driver_memory)

            # --files file:///home/hadoop/causality-analytics/EnsembleCausality/Journal/5v_linear_10M.csv \
            # two_phase_algorithm_data.py 3 5v_linear_10M.csv 240 3 -v')
    
    # while 1:
    #     time.sleep(5)
    #     try:
    #         conn.run("yarn application -list -appStates FINISHED | sed 's/^.*history//g' > appStates")
    #         break
    #     except:
    #         pass

    # conn.run("tail -n 1 appStates | cut -d '/' -f 2 > appID")
    # conn.run("sed -i '1s/^/yarn logs --applicationId /' appID")
    # conn.run('bash appID > %s'%experiment_name)
    # conn.get('%s'%experiment_name)

    # conn.run("rm appStates")
    # conn.run("rm appID")

@task
def getlog(conn):
    # yarn logs --applicationId application_
    conn.get('log')