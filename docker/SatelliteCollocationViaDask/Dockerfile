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
RUN pip3 install netCDF4 h5py pyhdf pandas numpy datetimerange

# Fetch satellite collocation code from its repository and install it
RUN git clone https://github.com/AI-4-atmosphere-remote-sensing/satellite_collocation
cd satellite_collocation
python3.6 setup.py install

#for dask
RUN python3.6 -m pip install "dask[complete]"
RUN pip3 uninstall -y click

WORKDIR /root/
