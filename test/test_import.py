from importlib import import_module


def test_import_cli():
    mod = import_module('apache_replay.script')
    dirmod = dir(mod)
    assert 'run' in dirmod
    assert 'main' in dirmod


def test_import():
    mod = import_module('apache_replay')
    dirmod = dir(mod)
    assert 'COMMON_LOG_PATTERN' in dirmod
    assert 'CommonLog' in dirmod
    assert 'Parser' in dirmod
    assert 'parse_entries_from' in dirmod
    assert 'Player' in dirmod
    assert 'RePlayer' in dirmod
    assert 'DryrunPlayer' in dirmod
