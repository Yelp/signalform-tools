FROM ubuntu:xenial

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdebi-core \
    software-properties-common \
    && apt-get clean

# Need Python 3.6
RUN add-apt-repository ppa:deadsnakes/ppa

WORKDIR /work
