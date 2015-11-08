#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Unittest for utils
PythonVersion: python2.7

Author: linzebin(linzebin@baidu.com)
CreateDate: 2015/10/9

Usage:
    python utils_test.py

"""
import sys
import unittest

sys.path.append('../')

import utils


class UtilsTestCase(unittest.TestCase):
    def test_url_to_file(self):
        """Test url_to_file function"""
        file_name = utils.url_to_filename('http://www.baidu.com')
        target_name = 'http:%2F%2Fwww.baidu.com'

        self.assertEqual(file_name, target_name)


if __name__ == "__main__":
    unittest.main()
