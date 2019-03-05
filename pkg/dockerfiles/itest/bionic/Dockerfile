FROM ubuntu:bionic

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdebi-core \
    xz-utils \
    && apt-get clean

WORKDIR /work
