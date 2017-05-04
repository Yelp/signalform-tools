FROM    docker-dev.yelpcorp.com/xenial_pkgbuild
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.4 && \
    apt-get clean
WORKDIR /work
