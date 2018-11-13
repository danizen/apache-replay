#!/usr/bin/env python
import re
from datetime import datetime
import attr


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


