FROM ubuntu:bionic

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
        python-pip \
        python-pkg-resources \
        python-setuptools \
        virtualenv \
        wget

WORKDIR /work
