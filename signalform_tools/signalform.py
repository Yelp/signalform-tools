# -*- coding: utf8 -*-
import argparse
import os

from signalform_tools.__about__ import __version__
from signalform_tools.preflight import preflight_signalform
from signalform_tools.show import show_signalform
from signalform_tools.validate import validate_signalform


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

    parser_preflight = subparsers.add_parser(
        'preflight',
        help='preflight help',
        description='Test your detector.')
    parser_preflight.add_argument('file', help='Path to tfstate file', type=str)
    parser_preflight.add_argument('--label', help='Specific detect label to test, checks all in the current folder by default', type=str)
    parser_preflight.add_argument('--start', help='Start time to check from. Can be either SignalFx relative time format (e.g. "-60m", "-3d", "-1w"), a date or a UNIX epoch timestamp in seconds or milliseconds', type=str)
    parser_preflight.add_argument('--stop', help='End time to check until. Can be either SignalFx relative time format (e.g. "Now", "-60m", "-3d"), a date or a UNIX epoch timestamp in seconds or milliseconds', type=str)
    parser_preflight.set_defaults(func=preflight_signalform)

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


if __name__ == "__main__":
    main()
