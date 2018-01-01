FROM ubuntu:xenial

RUN apt-get update > /dev/null && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
        bash \
        curl \
        vim-tiny \
        less \
        locales > /dev/null \
    && DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade > /dev/null \
    && apt-get clean > /dev/null

RUN /usr/sbin/locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# Need Python 3.6
RUN apt-get update > /dev/null && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa

WORKDIR /work
