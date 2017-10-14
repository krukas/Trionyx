#!/usr/bin/env python3
"""
run_test
~~~~~~~~

Test script that include Trionyx in path and auto discover tests.

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""

import os
import sys
import unittest

if __name__ == "__main__":
    try:
        import trionyx  # NOQA F401
    except Exception as e:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    testsuite = unittest.TestLoader().discover(os.path.dirname(os.path.realpath(__file__)))
    unittest.TextTestRunner(verbosity=1).run(testsuite)
