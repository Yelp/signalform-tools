# -*- coding: utf8 -*-
import argparse

from signalform_tools.__about__ import __version__


def parse_args():
    parser = argparse.ArgumentParser(
        description="signalform-tools has a lot of tools that can help you!"
    )
    parser.add_argument(
        '--version',
        action='version',
        version="signalform-tools {}".format(__version__)
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.command(args)
