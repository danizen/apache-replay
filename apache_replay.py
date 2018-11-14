#!/usr/bin/env python
import re
from datetime import datetime, timedelta
import time
import attr
import argparse
import glob
import sys


# Model

@attr.s(frozen=True)
class CommonLog(object):
    remote_host = attr.ib()
    remote_log_name = attr.ib()
    remote_user = attr.ib()
    timestamp = attr.ib(type=datetime)
    method = attr.ib()
    path = attr.ib()
    status = attr.ib(type=int)
    content_length = attr.ib(type=int)

    @property
    def ok(self):
       return self.status >= 200 and self.status < 300


# Parser

pattern = (r'(?P<remote_host>[^ ]+) '
           r'(?P<remote_log_name>[^ ]+) '
           r'(?P<remote_user>[^ ]+) '
           r'\[(?P<timestamp>[^\]]+)\] '
           r'"(?P<method>GET|POST|PUT|TRACE|OPTIONS|HEAD|DELETE) (?P<path>[^"]+)" '
           r'(?P<status>\d+) '
           r'(?P<content_length>\d+)')

expr = re.compile(pattern)

def parse_line(line):
    m = expr.match(line)
    if m:
        remote_log_name = m.group('remote_log_name')
        if remote_log_name == '-':
            remote_log_name = None
        remote_user = m.group('remote_user')
        if remote_user == '-':
            remote_user = None
        timestamp = datetime.strptime(m.group('timestamp'), '%d/%b/%Y:%H:%M:%S %z')
        status = int(m.group('status'))
        content_length = int(m.group('content_length'))
        return CommonLog(
            remote_host=m.group('remote_host'),
            remote_log_name=remote_log_name, 
            remote_user=remote_user,
            timestamp=timestamp,
            status=status,
            content_length=content_length,
            method=m.group('method'),
            path=m.group('path'),
        )


# CLI and main

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


def create_parser():
    parser = argparse.ArgumentParser(description='Read and replay Apache logs')
    parser.add_argument('target', metavar='URL',
                        help='The target URL where requests should be directed')
    parser.add_argument('path', metavar='PATH', nargs='+',
                        help='Glob expression for log or logs to replay')
    parser.add_argument('--start', metavar='TIMESTAMP', default=None, type=valid_datetime_type,
                        help='Minimum timestamp to start')
    parser.add_argument('--end', metavar='TIMESTAMP', default=None, type=valid_datetime_type,
                        help='Maximum timestamp when to stop')
    parser.add_argument('--count', metavar='NUMBER', default=None, type=int,
                        help='Maximum number of requests to generate')
    return parser


def parse_args(args):
    parser = create_parser()
    return parser.parse_args(args)


def run(target, path, start=None, end=None, count=None):
    path_list = sorted(glob.glob(path))
    if len(path_list) == 0:
        sys.stderr.write('No files found matching expression {}\n'.format(path))
    timestamp = None
    for path in path_list:
        with open(path, 'r') as f:
            for line in f:
                entry = parse_line(line)
                if start and timestamp < start:
                    continue
                if end and timestamp > end:
                    continue
                if timestamp is None:
                    timestamp = entry.timestamp
                delta = entry.timestamp - timestamp
                wait = delta.total_seconds()
                if wait > 0:
                    time.sleep(wait)
                print('{} {}'.format(entry.method, entry.path))


def main(args):
    opts = parse_args(args)
    run(**opts)


if __name__ == '__main__':
    main(sys.argv[1:])

