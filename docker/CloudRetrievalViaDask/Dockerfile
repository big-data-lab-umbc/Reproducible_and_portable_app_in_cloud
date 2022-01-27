FROM ubuntu:20.04

RUN apt update && apt install software-properties-common -y

RUN apt-get install -y python3-pip
RUN apt-get install -y git wget zip unzip vim curl

RUN pip3 install pandas sklearn numpy h5py

RUN pip3 install matplotlib seaborn tables datetimerange pyhdf netCDF4 pvlib

#for dask
RUN python3 -m pip install "dask[complete]"
RUN pip3 uninstall -y click
RUN pip3 install dask-ml click==7

WORKDIR /root/
