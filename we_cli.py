# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from __future__ import print_function

import argparse
import getpass
import logging
import os
import traceback
import sys
import pkg_resources

from colorlog import ColoredFormatter

from sawtooth_we.we_client import WeClient
from sawtooth_we.we_exceptions import WeException


DISTRIBUTION_NAME = 'sawtooth-we'


DEFAULT_URL = 'http://127.0.0.1:8008'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))



def add_set_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'set',
        help='function to put something on the BlockChain',
        description='Sends a transaction with the name corresponding to the date and hour of the recorded consumption',
        parents=[parent_parser])

    parser.add_argument(
        '-name',
        type=str,
        help='specify the date and hour of the recorded consumption (be carefull to NOT put spaceces on the name)')

    parser.add_argument(
        '-listId',
        type=int,
        nargs = '+',
        help='specify the Id of the consummer/producer separated by a space')
    
    parser.add_argument(
        '-listConsumption',
        type=int,
        nargs = '+',
        help='specify the consummtion of each participant separated by a space')


def add_get_parser(subparsers, parent_parser):
    parser = subparsers.add_parser(
        'get',
        help='function get that we create (under teset)',
        description='get for all the blocks created',
        parents=[parent_parser])

    parser.add_argument(
        '-name',
        type=str,
        help='specify the name of the energy community')







def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description=' ',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_set_parser(subparsers, parent_parser)
    add_get_parser(subparsers, parent_parser)

    return parser





def do_set(args):
    listId = args.listId
    listConsumption = args.listConsumption
    name = args.name

    url = _get_url(args)
    keyfile = _get_keyfile(args)
    client = WeClient(base_url=url, keyfile=keyfile)
    response = client.set(name, listId, listConsumption)
    print("Response: {}".format(response))


def do_get(args):
    url = _get_url(args)

    client = WeClient(base_url=url, keyfile=None)
    data = client.get(args.name)
    print("Response : ", data.decode("utf-8"))

    
    

def _get_url(args):
    return DEFAULT_URL

def _get_keyfile(args):
    username = "my_key"
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, username)


#argv[0] = nom du program. args = argv[1:]
#
def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    if args.command == 'set':
        do_set(args)
    elif args.command == 'get':
        do_get(args)
    else:
        raise WeException("invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except WeException as err:
        print("Error: {}".format(err), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
