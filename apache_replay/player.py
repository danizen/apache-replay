import attr
import sys

import requests

__all__ = (
    'Player',
    'RePlayer',
    'DryrunPlayer',
)


@attr.s
class Player(object):
    target = attr.ib(type=str)
    timeout = attr.ib(type=float, default=5.0)
    count = 0

    def after_play(self, elapsed, entry):
        pass

    def play(self, elapsed, entry):
        self.after_play(elapsed, entry)
        self.count += 1

class RePlayer(Player):

    def play(self, elapsed, entry):
        url = self.target + entry.path
        try:
            response = requests.request(entry.method, url, timeout=self.timeout, allow_redirects=False)
            if entry.status != response.status_code:
                sys.stderr.write('\n{}: status sb:{}, is:{}\n'.format(
                    url, entry.status, response.status_code))
            # we read the response data, but we don't care about it
            response.content
        except Exception as e:
            sys.stderr.write('\n{}'.format(str(e)))
        super().play(elapsed, entry)

    def after_play(self, elapsed, entry):
        sys.stdout.write('.')
        sys.stdout.flush()
        if ((self.count + 1) % 60) == 0:
            sys.stdout.write('\n')


class DryrunPlayer(Player):

    def after_play(self, elapsed, entry):
        url = self.target + entry.path
        print('{:-10d}s - {} {}'.format(int(elapsed), entry.method, url))
