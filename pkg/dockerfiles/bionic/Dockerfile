FROM ubuntu:bionic

# Don't run apt-get clean since gdebi will need those packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
        build-essential \
        debhelper \
        devscripts \
        dpkg-dev \
        equivs \
        gdebi-core \
        libcurl4-openssl-dev \
        libyaml-dev \
        python3-dev \
        python-pip \
        python-pkg-resources \
        python-setuptools \
        virtualenv \
        wget

RUN cd /tmp && \
    wget http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_1.0-1_all.deb && \
    gdebi -n dh-virtualenv*.deb && \
    rm dh-virtualenv_*.deb

WORKDIR /work
