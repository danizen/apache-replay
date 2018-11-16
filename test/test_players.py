from unittest import mock
import requests


def test_dryrun(entry):
    from apache_replay.player import DryrunPlayer
    player = DryrunPlayer('http://localhost:8000')
    assert player.count == 0

    with mock.patch(
            'apache_replay.player.requests.request',
            return_value=None) as mock_func:
        player.play(0.0, entry)
        mock_func.assert_not_called()
    assert player.count == 1

def test_count(entry):
    from apache_replay.player import Player
    player = Player('http://localhost:8000')
    assert player.count == 0

    with mock.patch(
            'apache_replay.player.requests.request',
            return_value=None) as mock_func:
        player.play(0.0, entry)
        mock_func.assert_not_called()
    assert player.count == 1


def test_replay(entry):
    from apache_replay.player import RePlayer
    player = RePlayer('http://www.google.com')
    assert player.count == 0

    with mock.patch(
            'apache_replay.player.requests.request',
            wraps=requests.request) as mock_func:
        player.play(0.0, entry)
        assert mock_func.call_count == 1
        method, url = mock_func.call_args[0]
        assert method == 'GET'
        assert url == 'http://www.google.com/'

        kwargs = mock_func.call_args[1]
        assert 'allow_redirects' in kwargs
        assert 'timeout' in kwargs
        assert kwargs['allow_redirects'] is False

    assert player.count == 1

