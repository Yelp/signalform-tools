FROM ubuntu:jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdebi-core \
    xz-utils \
    && apt-get clean

WORKDIR /work
