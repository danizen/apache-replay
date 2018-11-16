#!/usr/bin/env python3
from datetime import datetime
import time
import argparse
import glob
import sys
import os

from apache_replay import *


def valid_datetime_type(arg_datetime_str):
    """custom argparse type for user datetime values given from the command line"""
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%dT%H',
        '%Y-%m-%d',
    ]
    for format_str in formats:
        try:
            return datetime.strptime(arg_datetime_str, format_str)
        except ValueError:
            pass
    msg = "Given Datetime ({0}) not valid! Expected format, 'YYYY-mm-dd[THH[:MM[:SS]]]'".format(arg_datetime_str)
    raise argparse.ArgumentTypeError(msg)


def create_parser(progname=None):
    if progname:
        progname = os.path.basename(progname)
    parser = argparse.ArgumentParser(description='Read and replay Apache logs', prog=progname)
    parser.add_argument('target', metavar='URL',
                        help='The target URL where requests should be directed')
    parser.add_argument('path', metavar='PATH', nargs='+',
                        help='Glob expression for log or logs to replay')
    parser.add_argument('--rate', type=float, default=0.0,
                        help='How fast or slow to playback - 0 means as fast as you can.')
    parser.add_argument('--start', metavar='TIMESTAMP', default=None, type=valid_datetime_type,
                        help='Minimum timestamp to start')
    parser.add_argument('--end', metavar='TIMESTAMP', default=None, type=valid_datetime_type,
                        help='Maximum timestamp when to stop')
    parser.add_argument('--player', metavar='NAME', choices=['print','count','replay'], default='replay',
                        help='You can count log entries, print new urls, or replay the request')
    parser.add_argument('--count', metavar='NUMBER', default=None, type=int,
                        help='Maximum number of requests to generate')
    return parser


def run(player, paths, start=None, end=None, rate=0.0, max_count=None):
    path_list = []
    for pattern in paths:
        path_list += glob.glob(pattern)
    path_list = sorted(path_list)

    if len(path_list) == 0:
        sys.stderr.write(
            'No files found matching your path expression(s): {}\n'.format(','.join(paths))
        )
        sys.exit(1)

    elapsed = 0.0
    for entry in parse_entries_from(path_list, start=start, end=end, max_count=max_count):
        wait = rate * entry.delta
        if wait > 0:
            time.sleep(wait)
        elapsed += entry.delta
        player.play(elapsed, entry)

    print('\nTotal Count: {}'.format(player.count))


def main_args(args):
    parser = create_parser(args[0])
    opts = parser.parse_args(args[1:])

    target = opts.target
    if target.endswith('/'):
        target = target[:-1]
    if opts.player == 'print':
        player = DryrunPlayer(target)
    elif opts.player == 'count':
        player = Player(target)
    elif opts.player == 'replay':
        player = RePlayer(target)
    else:
        raise ValueError('Invalid value for opts.player')

    run(player, opts.path,
        start=opts.start,
        end=opts.end,
        rate=opts.rate,
        max_count=opts.count)

def main():
    return main_args(sys.argv)


if __name__ == '__main__':
    main()
