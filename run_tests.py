import os
import sys
import unittest

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mdbase')
)

tests = unittest.TestLoader().discover(start_dir="tests")
suite = unittest.TestSuite(tests)
runner = unittest.TextTestRunner()

if __name__ == "__main__":
    runner.run(suite)
