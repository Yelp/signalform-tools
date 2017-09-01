.PHONY: all changelog clean package tag test

PACKAGE_VERSION=$(shell python setup.py --version)
SYSTEM_PKG_NAME=signalform-tools
PYTHON_PKG_NAME=$(shell python setup.py --name)

ifdef PYPI_URL
TOX_PYPI_URL=-i $(PYPI_URL)
endif

all: test

changelog:
	if [ ! -f debian/changelog ]; then \
	    dch -v ${PACKAGE_VERSION} --create --package=$(SYSTEM_PKG_NAME) -D lucid -u low ${ARGS}; \
	else \
	    dch -v ${PACKAGE_VERSION} -D lucid -u low ${ARGS}; \
	fi
	git add debian/changelog

clean:
	git clean -fdx -- debian
	rm -f ./dist
	make -C build clean
	find . -iname '*.pyc' -delete
	rm -rf .tox

dist:
	ln -sf build/dist ./dist

itest_%: dist
	make -C build $@

package: itest_trusty itest_xenial

tag:
	git tag v${PACKAGE_VERSION}

test:
	tox $(TOX_PYPI_URL)
