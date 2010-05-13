"""
Tests for huxml.
"""
import unittest
import doctest

import huxml

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(huxml))
    runner = unittest.TextTestRunner()
    runner.run(suite)
