FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu16.04

CMD nvidia-smi

RUN apt-get update && \
    apt-get install -y sudo && \
    sudo apt-get install -y software-properties-common && \
    sudo add-apt-repository ppa:deadsnakes/ppa
RUN sudo apt-get update

RUN sudo apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-gdbm
RUN sudo apt-get install -y git wget curl zip unzip vim apt-utils gcc make libc-dev musl-dev g++

RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN python3.6 -m pip install --upgrade pip setuptools
RUN python3.6 -m pip install configargparse
RUN pip3 install tensorflow==2.2.0
RUN pip3 install cmake keras pandas sklearn numpy Cython

# Install OpenSSH to communicate between containers
RUN sudo apt-get install -y --no-install-recommends openssh-client openssh-server && \
    mkdir -p /var/run/sshd

# Setup SSH Daemon
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Allow OpenSSH to talk to containers without asking for confirmation
RUN cat /etc/ssh/ssh_config | grep -v StrictHostKeyChecking > /etc/ssh/ssh_config.new && \
    echo "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config.new && \
    mv /etc/ssh/ssh_config.new /etc/ssh/ssh_config

RUN sudo apt-get update && \
    sudo apt-get clean -y && sudo rm -rf /var/lib/apt/lists/*

#for DeepCoral (MultiGpus-Domain-Adaptation-main)
RUN wget https://download.open-mpi.org/release/open-mpi/v4.0/openmpi-4.0.0.tar.gz
RUN tar -xzvf openmpi-4.0.0.tar.gz
RUN cd openmpi-4.0.0/ && ./configure --prefix=/usr/local/ && sudo make all install

RUN sudo apt update
RUN wget https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64/libnccl-dev_2.4.7-1+cuda10.1_amd64.deb
RUN wget https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64/libnccl2_2.4.7-1+cuda10.1_amd64.deb
RUN sudo dpkg -i libnccl2_2.4.7-1+cuda10.1_amd64.deb
RUN sudo dpkg -i libnccl-dev_2.4.7-1+cuda10.1_amd64.deb

RUN pip3 install torch torchvision
RUN HOROVOD_WITH_PYTORCH=1 HOROVOD_GPU_OPERATIONS=NCCL HOROVOD_WITH_MPI=1 pip install --no-cache-dir horovod[pytorch]

RUN sudo cp /usr/local/cuda-10.1/compat/* /usr/local/cuda/lib64/

WORKDIR /root/