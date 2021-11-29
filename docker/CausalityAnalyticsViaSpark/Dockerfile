FROM amazoncorretto:8

RUN yum -y update
RUN yum -y install yum-utils
RUN yum -y groupinstall development

RUN yum list python3*
RUN yum -y install python3 python3-dev python3-pip python3-virtualenv python3-devel

RUN python -V
RUN python3 -V

ENV PYSPARK_DRIVER_PYTHON python3
ENV PYSPARK_PYTHON python3

RUN pip3 install --upgrade pip
RUN pip3 install numpy==1.16.2 scipy==1.2.0 pandas==0.24.1 scikit-learn==0.20.3 matplotlib networkx==1.11 cython setuptools pgmpy==0.1.6 statsmodels==0.9.0 wrapt 
RUN pip3 install --upgrade --force-reinstall setuptools

RUN git clone https://github.com/Pei427/tigramite.git 
WORKDIR "/tigramite"
RUN python3 setup.py install

RUN amazon-linux-extras enable R3.4
RUN yum -y install R R-devel openssl-devel openssl libssh2-devel libssl-dev libcurl-devel libxml2-devel 
RUN yum -y install curl curl-devel curl-dev curl-config 
RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.us.r-project.org'; options(repos = r);" > ~/.Rprofile

RUN Rscript -e "install.packages('MASS',dependencies = TRUE)"
RUN Rscript -e "install.packages('momentchi2',dependencies = TRUE)"
RUN Rscript -e "install.packages('devtools')"
RUN Rscript -e "library(devtools)"
RUN Rscript -e "devtools::install('external_packages/RCIT')"

RUN pip3 install rpy2==3.3.2

RUN python3 -c "import numpy as np"
RUN python3 -c "import pandas"
Run python3 -c "print(pandas.__version__)"
