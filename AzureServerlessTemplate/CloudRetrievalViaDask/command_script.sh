#!/bin/bash

docker pull starlyxxx/dask-decision-tree-example
wget -P /home/azureuser/ https://kddworkshop.s3.us-west-2.amazonaws.com/ML_based_Cloud_Retrieval_Use_Case.zip
unzip /home/azureuser/ML_based_Cloud_Retrieval_Use_Case.zip -d /home/azureuser/

docker run -v /home/azureuser/ML_based_Cloud_Retrieval_Use_Case:/root/ML_based_Cloud_Retrieval_Use_Case starlyxxx/dask-decision-tree-example:latest sh -c 'cd ML_based_Cloud_Retrieval_Use_Case/Code && /usr/bin/python3.6 ml_based_cloud_retrieval_with_data_preprocessing.py' | tee -a /home/azureuser/result.txt
