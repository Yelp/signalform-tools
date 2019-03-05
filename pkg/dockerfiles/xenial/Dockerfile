FROM ubuntu:xenial

# Need Python 3.6
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
        build-essential \
        debhelper \
        devscripts \
        dpkg-dev \
        equivs \
        gdebi-core \
        libcurl4-openssl-dev \
        libyaml-dev \
        python-dev \
        python3.6-dev \
        python-pip \
        python-pkg-resources \
        python-setuptools \
        wget \
    && apt-get clean

RUN cd /tmp && \
    wget http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_1.0-1_all.deb && \
    gdebi -n dh-virtualenv*.deb && \
    rm dh-virtualenv_*.deb

WORKDIR /work
