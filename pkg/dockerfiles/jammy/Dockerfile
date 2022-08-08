FROM ubuntu:jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

# Don't run apt-get clean since gdebi will need those packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
        build-essential \
        debhelper \
        devscripts \
        dh-virtualenv \
        dpkg-dev \
        equivs \
        gdebi-core \
        libcurl4-openssl-dev \
        libyaml-dev \
        python3.8 \
        python3.8-dev \
        python3.8-distutils \
        virtualenv \
        wget

WORKDIR /work
