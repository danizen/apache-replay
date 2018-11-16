import re
from pprint import pprint
import pytest


def test_pattern_matches_all(lines):
    from apache_replay import COMMON_LOG_PATTERN as pattern
    for line in lines:
        m = re.match(pattern, line)
        assert m is not None
        values = m.groupdict()
        assert isinstance(values, dict)
        pprint(values)


def test_parses_all(lines):
    from apache_replay import Parser, CommonLog
    parser = Parser()
    for line in lines:
        entry = parser.parse(line)
        assert isinstance(entry, CommonLog)


def test_raises_with(badlines):
    from apache_replay import Parser, ParserException
    parser = Parser()
    with pytest.raises(ParserException):
        for line in badlines:
            parser.parse(line)


def test_entry_generator_parses_all_from(somelines_path):
    from apache_replay import parse_entries_from, CommonLog
    entries = list(parse_entries_from([somelines_path]))
    assert len(entries) == 3
    assert all(isinstance(entry, CommonLog) for entry in entries)


def test_entry_generator_raises_from(badlines_path):
    from apache_replay import parse_entries_from, ParserException
    with pytest.raises(ParserException):
        list(parse_entries_from([badlines_path]))


