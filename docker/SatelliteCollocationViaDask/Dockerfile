FROM ubuntu:20.04

RUN apt update && apt install software-properties-common -y

RUN apt-get install -y python3-pip
RUN apt-get install -y git wget zip unzip vim curl

RUN python3 -m pip install pip --upgrade
RUN python3 -m pip install wheel

RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install configargparse
RUN pip3 install netCDF4 h5py pyhdf pandas numpy datetimerange

# Fetch satellite collocation code from its repository and install it
RUN wget -P /home/ubuntu/ https://ai-4-atmosphere-remote-sensing.s3.amazonaws.com/satellite_collocation-main.zip
RUN unzip /home/ubuntu/satellite_collocation-main.zip -d /home/ubuntu/
WORKDIR /home/ubuntu/satellite_collocation-main/
RUN python3 setup.py install

#for dask
RUN python3 -m pip install "dask[complete]"
RUN pip3 uninstall -y click

WORKDIR /root/
