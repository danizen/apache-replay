import re
from datetime import datetime
import attr
import sys

__all__ = (
    'CommonLog',
    'ParserException',
    'COMMON_LOG_PATTERN',
    'Parser',
    'parse_entries_from',
)

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


def parse_entries_from(path_list, start=None, end=None, max_count=None):
    """
    yield CommonLog (also combined) log entries from paths in the path list until done.
    Filtering is done using start, end, and max_count
     
    :param path_list: A sequence of glob expressions or a string containing such  
    :param start: a datetime representing the earliest datetime to be sent
    :param end: a datetime representing the latest datetime to be sent
    :param max_count: An integer indicating the maximum number of logs to be sent
    :return:  a generator that generates ``CommonLog`` instances
    """
    parser = Parser()
    if max_count is None:
        max_count = sys.maxsize
    tot_count = 0
    if isinstance(path_list, str):
        path_list = [path_list]
    for path in path_list:
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
