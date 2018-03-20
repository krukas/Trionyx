"""
trionyx.utils
~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import random
import string


def random_string(size):
    """Create random string containing ascii leters and digits, with the length of given size"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))
