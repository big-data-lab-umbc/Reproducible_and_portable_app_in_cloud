# Reproducible and Portable Big Data Analytics in Cloud

## Introduction
We implement the Reproducible and Portable big data Analytics in the Cloud (RPAC) Toolkit, which help us deploy, execute, analyze, and reproduce big data analytics automatically in cloud. 

### Abstract
Cloud computing has become a major approach to enable reproducible computational experiments because of its support of on-demand hardware and software resource provisioning. Yet there are still two main difficulties in reproducing big data applications in the cloud. The first is how to automate end-to-end execution of big data analytics in the cloud including virtual distributed environment provisioning, network and security group setup, and big data analytics pipeline description and execution. The second is an application developed for one cloud, such as AWS or Azure, is difficult to reproduce in another cloud, a.k.a. vendor lock-in problem. To tackle these problems, we leverage serverless computing and containerization techniques for automatic scalable big data application execution and reproducibility, and utilize the adapter design pattern to enable application portability and reproducibility across different clouds. Based on the approach, we propose and develop an open-source toolkit that supports 1) on-demand distributed hardware and software environment provisioning, 2) automatic data and configuration storage for each execution, 3) flexible client modes based on user preferences, 4) execution history query, and 5) simple reproducibility of existing executions in the same environment or a different environment. We did extensive experiments on both AWS and Azure using three big data analytics applications that run on a virtual CPU/GPU cluster. Three main behaviors of our toolkit were benchmarked: i) execution overhead ratio for reproducibility support, ii) differences of reproducing the same application on AWS and Azure in terms of execution time, budgetary cost and cost-performance ratio, iii) differences between scale-out and scale-up approach for the same application on AWS and Azure.

## Install
```bash
pip3 install configparser
pip3 install aws-sam-cli
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

## Usage
To use RPAC toolkit, make the following changes to your configuration:

1. Update configurations [resource.ini](./ConfigTemplate/resource.ini), [application.ini](./ConfigTemplate/application.ini), [personal.ini](./ConfigTemplate/personal.ini) in ConfigTemplate folder.
2. Run ```python3 main.py``` to execute the big data analytics.

## Examples
The examples folder includes configuration examples of our three proposed parallel frameworks. To running the examples, just directly copy these example configurations to ConfigTemplate folder.

## Reproduce
The reproduce folder includes the generated pipeline file. RPAC toolkit will execute big data analytics in cloud based on the files in this folder.
