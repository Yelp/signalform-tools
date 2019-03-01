# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from signalform_tools.__about__ import __version__


setup(
    name='signalform-tools',
    version=__version__,
    provides=["signalform_tools"],
    author='',
    author_email='',
    description='',
    packages=find_packages(exclude=["tests"]),
    setup_requires=['setuptools'],
    include_package_data=True,
    install_requires=[
        'boto3',
        'requests',
        'python-dateutil'
    ],
    entry_points={
        'console_scripts': [
            'signalform-tools=signalform_tools.signalform:main',
        ],
    },
)
