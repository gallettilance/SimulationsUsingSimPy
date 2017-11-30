FROM ubuntu

MAINTAINER Lance Galletti

COPY . /src
WORKDIR /src

RUN apt-get update && \
    apt-get install -y python2.7 && \
    apt-get install -y python-pip && \
    pip install -r requirements.txt && \
    apt-get install -y python-tk
    