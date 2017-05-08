FROM    docker-dev.yelpcorp.com/trusty_pkgbuild
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.6 && \
    apt-get clean
WORKDIR /work
