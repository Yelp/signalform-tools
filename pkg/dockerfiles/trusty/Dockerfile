FROM ubuntu:trusty

RUN apt-get update > /dev/null && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
        bash \
        curl \
        vim-tiny \
        less > /dev/null \
    && DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade > /dev/null \
    && apt-get clean > /dev/null

RUN /usr/sbin/locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# Need Python 3.6
RUN apt-get update > /dev/null && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:fkrull/deadsnakes

RUN apt-get update > /dev/null && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
        build-essential \
        debhelper \
        devscripts \
        dpkg-dev \
        equivs \
        gdebi-core \
        git \
        libcurl4-openssl-dev \
        libyaml-dev \
        python-dev \
        python3.6-dev \
        python-pip \
        python-pkg-resources \
        python-setuptools \
        python-tox \
        rpm \
        ruby \
        ruby-dev \
        wget > /dev/null \
    && apt-get clean > /dev/null

RUN cd /tmp && \
    wget http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_1.0-1_all.deb && \
    gdebi -n dh-virtualenv*.deb && \
    rm dh-virtualenv_*.deb

RUN pip install virtualenv==15.1.0

RUN gem install fpm

WORKDIR /work
