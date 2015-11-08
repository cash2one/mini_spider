#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
Unittest for objects

Author: linzebin(linzebin@baidu.com)
CreateDate: 2015/10/9

Usage:
    python objects_test.py

"""
import os
import sys
import urllib2
import shutil 
import unittest

import Queue

sys.path.append('../')

import objects
import mini_spider


class ObjectsTestCase(unittest.TestCase):
    def test_url(self):
        """test Url object"""
        url1 = objects.Url('http://www.baidu.com', 1)
        url2 = objects.Url('http://www.baidu.com', 2)
        url3 = objects.Url('http://www.sina.com', 1)
        url_set = set([url1, url2, url3])

        self.assertEqual(url1, url2)
        self.assertEqual(len(url_set), 2)
        self.assertEqual(url1 in url_set, True)

    def test_page_parser(self):
        """test PageParser object"""
        test_url = objects.Url('http://pycm.baidu.com:8081', 1)
        page = urllib2.urlopen(test_url.url).read()
        parser = objects.PageParser(test_url, page)
        url_list = parser.parse()

        target_urls = [objects.Url('http://page1.html', 2),
                    objects.Url('http://page2.html', 2),
                    objects.Url('http://page3.html', 2),
                    objects.Url('http://mirror/index.html', 2),
                    objects.Url('http://pycm.baidu.com:8081/page4.html', 2)]

        self.assertEqual(url_list, target_urls)

    def test_spider(self):
        """Test Spider object"""
        # Inits
        temp_output = './temp_output'
        os.mkdir(temp_output)
        test_config = {'output_dir': temp_output,
                       'crawl_timeout': 5}
        test_url = objects.Url('http://www.baidu.com', 1)
        test_queue = Queue.Queue()
        test_exist_set = set()
        
		# Inits object
        spider = mini_spider.Spider(test_url, test_queue, test_exist_set, test_config)
        page = spider.get_page()

        spider.save_page(page, test_config['output_dir'])
    
        target_file = 'http:%2F%2Fwww.baidu.com'
        self.assertEqual(os.path.exists(os.path.join(temp_output, target_file)), True)

        shutil.rmtree(temp_output, True)


if __name__ == "__main__":
    unittest.main()
