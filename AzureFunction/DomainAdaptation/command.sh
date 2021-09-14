#!/bin/bash

docker pull starlyxxx/horovod-pytorch-cuda10.1-cudnn7
wget -P /home/azureuser/ https://kddworkshop.s3.us-west-2.amazonaws.com/MultiGpus-Domain-Adaptation-main.zip
wget -P /home/azureuser/ https://kddworkshop.s3.us-west-2.amazonaws.com/office31.tar.gz
unzip /home/azureuser/MultiGpus-Domain-Adaptation-main.zip -d /home/azureuser/
tar -xzvf /home/azureuser/office31.tar.gz  -C /home/azureuser/

nvidia-docker run -v /home/azureuser/MultiGpus-Domain-Adaptation-main:/root/MultiGpus-Domain-Adaptation-main -v /home/azureuser/office31:/root/office31 starlyxxx/horovod-pytorch-cuda10.1-cudnn7:latest sh -c 'cd MultiGpus-Domain-Adaptation-main && horovodrun --verbose -np 1 -H localhost:1 /usr/bin/python3.6 main.py --config DeepCoral/DeepCoral.yaml --data_dir ../office31 --src_domain webcam --tgt_domain amazon'  | tee -a /home/azureuser/result.txt
