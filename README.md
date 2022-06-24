# Reproducible and Portable Big Data Analytics in Cloud

## Introduction
We implement the Reproducible and Portable big data Analytics in the Cloud (RPAC) Toolkit, which help us deploy, execute, analyze, and reproduce big data analytics automatically in cloud. 

### Abstract
Cloud computing has become a major approach to enable reproducible computational experiments because of its support of on-demand hardware and software resource provisioning. Yet there are still two main difficulties in reproducing big data applications in the cloud. The first is how to automate end-to-end execution of big data analytics in the cloud including virtual distributed environment provisioning, network and security group setup, and big data analytics pipeline description and execution. The second is an application developed for one cloud, such as AWS or Azure, is difficult to reproduce in another cloud, a.k.a. vendor lock-in problem. To tackle these problems, we leverage serverless computing and containerization techniques for automatic scalable big data application execution and reproducibility, and utilize the adapter design pattern to enable application portability and reproducibility across different clouds. Based on the approach, we propose and develop an open-source toolkit that supports 1) on-demand distributed hardware and software environment provisioning, 2) automatic data and configuration storage for each execution, 3) flexible client modes based on user preferences, 4) execution history query, and 5) simple reproducibility of existing executions in the same environment or a different environment. We did extensive experiments on both AWS and Azure using three big data analytics applications that run on a virtual CPU/GPU cluster. Three main behaviors of our toolkit were benchmarked: i) execution overhead ratio for reproducibility support, ii) differences of reproducing the same application on AWS and Azure in terms of execution time, budgetary cost and cost-performance ratio, iii) differences between scale-out and scale-up approach for the same application on AWS and Azure.

## Prerequisite
RPAC currently supports `Python>=3.6`.

## Install Dependencies
```bash
pip3 install configparser
```
> Optional dependencies, only for AWS-based execution. Commands for other OSs are at [AWS User Guilde](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html): 
> ```bash
> pip3 install aws-sam-cli
> curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && sudo ./aws/install
> ```
> Optional dependencies, only for Azure-based execution: 
> ```bash
> curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
> ```

Set your credentials and other configurations for cloud platforms: 

For AWS: `aws configure set aws_access_key_id <aws_access_key> && aws configure set aws_secret_access_key <aws_secert_key> && aws configure set default.region us-west-2` 

For Azure: `az login`

## Usage

- `main.py` To perform RPAC of an experiment on a cloud.

```
usage: python3 main.py [-h] [--execution_history EXECUTION_HISTORY] [--one_click]
               [--terminate]

RPAC Toolkit.

optional arguments:
  -h, --help            show this help message and exit
  --execution_history EXECUTION_HISTORY
                        Folder name of execution history to reproduce, or
                        URI of execution history.
  --one_click           Allow one_click execution to be used by RPAC, implies
                        '--one_click'. Note this argument will terminate all
                        cloud resources after execution finished.
  --terminate           Terminate all cloud resources, implies '--terminate'.
```

To use RPAC toolkit, make the following changes to your configuration:

1. Update configurations [resource.ini](./ConfigTemplate/resource.ini), [application.ini](./ConfigTemplate/application.ini), [personal.ini](./ConfigTemplate/personal.ini) in ConfigTemplate folder.
  - For resource.ini: **reproduce_storage** is the S3 Bucket name, which will store all reproduction historical files. You need to create your bucket before running RPAC. We recommend a name only with lowercase letters, numbers, and hyphens (-). The detailed Bucket naming rules can be find in [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html).
  - For personal.ini: **cloud_credentials** is the key:value pair of your cloud credentials (Access key ID:Secret key ID). In order to find your credentials, see [here](https://console.aws.amazon.com/iam/home?region=us-west-2#security_credential).
3. Run ```python3 main.py``` to execute the big data analytics.

Example usage: `python3 main.py --one_click`, `python3 main.py --execution_history 0ec2088f-a3b8-4730-8e76-cac2015c74df --one_click`, `python3 main.py --execution_history s3://aws-sam-cli-managed-default-samclisourcebucket-xscicpwnc0z3/a57f212d-c7c3-46eb-ace4-d62bb6b294f6 --one_click`.

For a closer look, please refer to our [demo](https://www.youtube.com/watch?v=Jzid0E89SrU).

## Getting Started
Three-pointers for experimental execution to get you started:
- [First execution: get first execution with understanding and using RPAC toolkit](./docs/first_execution.md)
- [Examples: easy to understand RPAC across three applications](./docs/examples.md)
- [Reproduce: reproduce existing execution with RPAC](./docs/reproduce.md)
- [New application: create your own applications with RPAC](./docs/newapplication.md)

End-to-end execution also provided in RPAC:
- [End-to-end: one-click execution with RPAC](./docs/end_to_end.md)

## Citation
If you use this code for your research, please cite our [paper](https://arxiv.org/abs/2112.09762):

```
@misc{wang2021reproducible,
      title={Reproducible and Portable Big Data Analytics in the Cloud}, 
      author={Xin Wang and Pei Guo and Xingyan Li and Jianwu Wang and Aryya Gangopadhyay and Carl E. Busart and Jade Freeman},
      year={2021},
      eprint={2112.09762},
      archivePrefix={arXiv},
      primaryClass={cs.DC}
}
```
