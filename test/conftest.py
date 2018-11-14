from os import path
from pytest import fixture
from datetime import datetime


__all__ = (
    'DATA_DIR',
    'somelines_path',
    'badlines_path',
    'lines',
    'badlines',
    'entry',
)


DATA_DIR = path.join(path.dirname(__file__), 'data')


@fixture
def somelines_path():
    return path.join(DATA_DIR, 'somelines')


@fixture
def badlines_path():
    return path.join(DATA_DIR, 'badlines')


@fixture
def lines():
    with open(path.join(DATA_DIR, 'somelines')) as f:
        return [l for l in f]


@fixture
def badlines():
    with open(path.join(DATA_DIR, 'badlines')) as f:
        return [l for l in f]


@fixture
def entry():
    from apache_replay import CommonLog
    return CommonLog(
        remote_host='127.0.0.1',
        timestamp=datetime.now(),
        status=200,
        content_length=2022,
        method='GET',
        path='/',
    )
