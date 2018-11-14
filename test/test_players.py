from datetime import datetime
from unittest import mock
from urllib.request import urlopen, Request


def test_dryrun(entry):
    from apache_replay import DryrunPlayer
    player = DryrunPlayer('http://localhost:8000')

    with mock.patch('apache_replay.urlopen', return_value=None) as mock_func:
        player.play(0.0, entry)
        mock_func.assert_not_called()


def test_real(entry):
    from apache_replay import Player
    player = Player('http://www.google.com')

    with mock.patch('apache_replay.urlopen', wraps=urlopen) as mock_func:
        player.play(0.0, entry)
        assert mock_func.call_count == 1
        request ,= mock_func.call_args[0]
        assert isinstance(request, Request)
        assert request.method == 'GET'
        assert request.full_url == 'http://www.google.com/'
    
