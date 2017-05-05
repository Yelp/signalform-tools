# -*- coding: utf8 -*-
import argparse
import os

from signalform_tools.__about__ import __version__
from signalform_tools.validate import validate_signalform
from signalform_tools.show import show_signalform


def parse_args():
    parser = argparse.ArgumentParser(
        description="signalform-tools is a command line \
        with cool features built for signalform"
    )
    parser.add_argument(
        '--version',
        action='version',
        version="signalform-tools {}".format(__version__)
    )
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    parser_validate = subparsers.add_parser(
        'validate',
        help='validate help',
        description='Validate resources inside one or more directories.')
    parser_validate.add_argument('filenames', nargs='*')
    parser_validate.add_argument('--dir',
                                 help='directory to validate',
                                 default=os.getcwd())
    parser_validate.set_defaults(func=validate_signalform)

    parser_show = subparsers.add_parser(
        'show',
        help='show help',
        description="Show resources inside the \
            tfstate of the current directory.")
    parser_show.set_defaults(func=show_signalform)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)
