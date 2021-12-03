FROM ubuntu:16.04

RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-gdbm python3-setuptools
RUN apt-get install -y git wget zip unzip vim curl

RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN python3.6 -m pip install --upgrade pip setuptools
RUN python3.6 -m pip install configargparse
RUN pip3 install pandas sklearn numpy h5py

#commands for ml_based_cloud_retrieval_with_data_preprocessing only (line 1-20)
RUN pip3 install matplotlib seaborn tables datetimerange pyhdf netCDF4 pvlib

#for dask
RUN python3.6 -m pip install "dask[complete]"
RUN pip3 uninstall -y click
RUN pip3 install dask-ml click==7

WORKDIR /root/