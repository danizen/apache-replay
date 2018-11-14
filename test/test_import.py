from importlib import import_module


def test_import():
    mod = import_module('apache_replay')
    dirmod = dir(mod)
    assert 'COMMON_LOG_PATTERN' in dirmod
    assert 'CommonLog' in dirmod
    assert 'Parser' in dirmod
    assert 'Player' in dirmod
    assert 'DryrunPlayer' in dirmod

