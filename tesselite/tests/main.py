import os.path
import unittest
from pathlib import Path

def runSuite():
    tests_dir = Path(os.path.dirname(__file__))
    tests = unittest.TestLoader()
    suite = tests.discover(tests_dir.as_posix())
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    runSuite()
