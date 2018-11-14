#!/usr/bin/env python3
import re
from datetime import datetime, timedelta
import time
import attr
import argparse
import glob
import sys

from urllib.request import Request, urlopen


# Model

@attr.s(frozen=True)
class CommonLog(object):
    remote_host = attr.ib()
    timestamp = attr.ib(type=datetime)
    method = attr.ib()
    path = attr.ib()
    status = attr.ib(type=int)

    remote_log_name = attr.ib(default=None, repr=False)
    remote_user = attr.ib(default=None, repr=False)
    protocol = attr.ib(default=None, repr=False)
    content_length = attr.ib(type=int, default=0, repr=False)
    delta = attr.ib(type=int, default=0, repr=False)

    @property
    def ok(self):
       return self.status >= 200 and self.status < 300


# Line Parser


class ParserException(ValueError):
    """
    An error parsing a log file
    """
    def __init__(self, path=None, line=None):
        if path and line:
            msg = '{}:{} - parser encountered an error'.format(path, line)
        else:
            msg = 'parser encountered an error'
        super().__init__(msg)



COMMON_LOG_PATTERN = (r'(?P<remote_host>[^ ]+) '
                      r'(?P<remote_log_name>[^ ]+) '
                      r'(?P<remote_user>[^ ]+) '
                      r'\[(?P<timestamp>[^\]]+)\] '
                      r'"(?P<request_first_line>.(?:(?:(.(?!"))*)\\")*(?:[^"]+))" '
                      r'(?P<status>[\d-]+) '
                      r'(?P<content_length>[\d-]+)')


class Parser(object):
    last_timestamp = None
    elapsed = 0.0
    expr = re.compile(COMMON_LOG_PATTERN)
    
    def parse(self, line):
        m = self.expr.match(line)
        if not m:
            raise ParserException()
        if m:
            remote_log_name = m.group('remote_log_name')
            if remote_log_name == '-':
                remote_log_name = None
            remote_user = m.group('remote_user')
            if remote_user == '-':
                remote_user = None
            timestamp = datetime.strptime(m.group('timestamp'), '%d/%b/%Y:%H:%M:%S %z')
            if self.last_timestamp is None:
                self.last_timestamp = timestamp
            delta = int((timestamp - self.last_timestamp).total_seconds())
            self.last_timestamp = max(self.last_timestamp, timestamp)
            status = int(m.group('status')) if m.group('status') != '-' else None
            content_length = int(m.group('content_length')) if m.group('content_length') != '-' else None
            first_line = m.group('request_first_line').split(' ')
            if len(first_line) == 2:
                method, path = first_line
                protocol = None
            else:
                method, path, protocol = first_line
            return CommonLog(
                remote_host=m.group('remote_host'),
                remote_log_name=remote_log_name, 
                remote_user=remote_user,
                timestamp=timestamp,
                status=status,
                content_length=content_length,
                method=method,
                path=path,
                protocol=protocol,
                delta=delta,
            )


def entries_from(pathlist, start=None, end=None, max_count=None):
    parser = Parser()
    if max_count is None:
        max_count = sys.maxsize
    tot_count = 0
    if isinstance(pathlist, str):
        pathlist = [pathlist]
    for path in pathlist:
        if tot_count >= max_count:
            break
        with open(path, 'r') as f:
            lineno = 0
            for line in f:
                lineno += 1   
                try: 
                    entry = parser.parse(line)
                    if start and entry.timestamp < start:
                        continue
                    if end and entry.timestamp > end:
                        continue
                    if entry.method not in ('GET', 'HEAD', 'OPTIONS'):
                        continue
                    tot_count += 1
                    yield entry
                    if tot_count >= max_count:
                        break
                except Exception as e:
                    raise ParserException(path, lineno) from e
    

# Players - do something with the logs

@attr.s(frozen=True)
class Player(object):
    target = attr.ib(type=str)
    timeout = attr.ib(type=int, default=5.0)

    def play(self, elapsed, entry):
        url = self.target + entry.path
        request = Request(url, method=entry.method)
        with urlopen(request, timeout=self.timeout) as response:
            assert entry.status == response.getcode()



class DryrunPlayer(Player):

    def play(self, elapsed, entry):
        url = self.target + entry.path
        print('{:-10d}s - {} {}'.format(int(elapsed), entry.method, url))


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


def create_cli_parser():
    parser = argparse.ArgumentParser(description='Read and replay Apache logs')
    parser.add_argument('target', metavar='URL',
                        help='The target URL where requests should be directed')
    parser.add_argument('path', metavar='PATH', nargs='+',
                        help='Glob expression for log or logs to replay')
    parser.add_argument('--dryrun', default=False, action='store_true',
                        help='Only print the actions that will be taken')
    parser.add_argument('--rate', type=float, default=0.0,
                        help='How fast or slow to playback')
    parser.add_argument('--start', metavar='TIMESTAMP', default=None, type=valid_datetime_type,
                        help='Minimum timestamp to start')
    parser.add_argument('--end', metavar='TIMESTAMP', default=None, type=valid_datetime_type,
                        help='Maximum timestamp when to stop')
    parser.add_argument('--count', metavar='NUMBER', default=None, type=int,
                        help='Maximum number of requests to generate')
    return parser


def run(player, paths, start=None, end=None, rate=0.0, max_count=None):
    path_list = []
    for pattern in paths:
        path_list += glob.glob(pattern)
    path_list = sorted(path_list)

    if len(path_list) == 0:
        sys.stderr.write('No files found matching expression {}\n'.format(path))

    elapsed = 0.0
    for entry in entries_from(path_list, start=start, end=end, max_count=max_count):
        wait = rate * entry.delta
        if wait > 0:
            time.sleep(wait)
        elapsed += entry.delta
        player.play(elapsed, entry)


def main(args):
    parser = create_cli_parser()
    opts = parser.parse_args(args)

    target = opts.target
    if target.endswith('/'):
        target = target[:-1]
    if opts.dryrun:
        player = DryrunPlayer(target)
    else:
        player = Player(target)

    run(player, opts.path,
        start=opts.start,
        end=opts.end,
        rate=opts.rate,
        max_count=opts.count)


if __name__ == '__main__':
    main(sys.argv[1:])

