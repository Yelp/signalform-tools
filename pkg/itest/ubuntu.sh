#!/bin/bash

set -e

cd /

highlight() {
  echo -n "$(tput setaf 3)"
  echo -n "$@"
  echo "$(tput op)"
}

highlight_exec() {
  highlight "$@"
  command "$@"
  return $?
}

PACKAGE_NAME="$1"
PACKAGE_VERSION="$2"

# This will get DISTRIB_CODENAME
source /etc/lsb-release

# This will set us up to install our package through apt-get
highlight "Creating new apt source"

highlight_exec apt-get update

# The package should install ok
highlight_exec gdebi -n /dist/${DISTRIB_CODENAME}/${PACKAGE_NAME}_${PACKAGE_VERSION}_amd64.deb


${PACKAGE_NAME} --version

highlight "$0:" 'success!'
