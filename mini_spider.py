#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provides main entrance of mini-spider with multi-thread.

Author: linzebin(linzebin@baidu.com)
Date:   2015/9/26

Usage:
    python mini_spider.py -c spider.conf
"""
import os
import re
import time
import threading
import logging
import urllib2
import argparse

import Queue

import objects
import utils


VERSION = 1.0


class SpiderManager(object):
    """
    Spider work manager
    
    Attributes:
        threads: A list of spider threads
        url_queue: A queue of Url objects which waitting to be crawled
        exist_url_set: A set of Url objects which are crawled
        configs: A dictionary of configuration

    """
    def __init__(self, url_queue, thread_num=4, configs=None):
        """Init WorkManager with thread_num and configuration"""
        self.threads = []
        self.url_queue = url_queue
        self.exist_url_set = set()
        self.configs = configs
        self.__init_thread_pool(thread_num)
    
    def __init_thread_pool(self, thread_num):
        """Init thread pool with thread_num to 
            limit the number of SpiderThread"""
        for i in range(thread_num):
            spider_thread = SpiderThread(i, self.url_queue, self.exist_url_set, self.configs)
            spider_thread.start()   # start spider
            self.threads.append(spider_thread)
    
    def wait_all_complete(self):
        """Check whether all SpiderThread is alive"""
        for spider in self.threads:
            if spider.isAlive():
                spider.join()


class SpiderThread(threading.Thread):
    """
    SpiderThread class to execute Spider-process
    
    Attributes:
        idx: An index of spider thread
        _queue: A queue of Url objects which are watting to be crawled
        _exist_set: A set of Url objects which are crawled
        configs: A dictionary of configuration
    """
    def __init__(self, thread_idx, work_queue, exist_set, configs):

        """
        Init SpiderThread with thread_idx, work_queue and configs
        """
        threading.Thread.__init__(self)  # Call init func of Thread class
        self._queue = work_queue
        self._exist_set = exist_set
        self.configs = configs
        self.idx = thread_idx

    def run(self):
        """Overwrite run function of threading.Thread"""
        while True:
            try:
                """Doing job"""
                logging.info("Thread %s getting job url from work_queue" % self.idx)
                url = self._queue.get(block=True, timeout=self.configs['crawl_timeout'] * 5)

                """Crawl page from website"""
                spider = Spider(url, self._queue, self._exist_set, self.configs)
                spider.do_all_jobs()

                """Notify queue when job done"""
                self._queue.task_done()

                """Thread sleep for next crawl"""
                time.sleep(self.configs['crawl_interval'])

            except Queue.Empty:
                logging.info("Spider thread %s finished with queue empty." % self.idx)
                return

            except Exception as err:
                log_info = "Exception caught. ERROR:%s"
                logging.error(log_info % err)


class Spider(object):
    """
    Main spider process

    Attribute:
        url : Basic url info, objects.Url. Containing url and depth 
        configs : A dictionary of configurations 
        url_queue: A queue of Url objects which are watting to be crawled
        exist_set: A set of Url objects which are crawled
    """
    def __init__(self, url, url_queue, exist_set, configs):
        """
        Initiation of spider
        """
        self.url_queue = url_queue
        self.exist_set = exist_set
        self.url = url
        self.configs = configs

    def do_all_jobs(self):
        """
        Run spider all jobs.
            Get_page -> parse_page -> save_page
        """
        try:
            page = self.get_page()
            self.parse_page(page)
            save_pattern = re.compile(self.configs['target_url'])
            if save_pattern.findall(self.url.url):
                save_path = self.configs['output_dir']
                self.save_page(page, save_path)

            crawl_interval = self.configs['crawl_interval']

        except Exception as err:
            logging.error("Getting page failed, url:%s\n%s" % (self.url.url, err))

    def get_page(self):
        """
        Get html page from Internet

        Returns:
            A html page of url
        
        Raises:
            Exception: An error occurred failing in getting page with url
        """
        _timeout = self.configs['crawl_timeout']

        try:
            url_response = urllib2.urlopen(self.url.url, timeout=_timeout)
            _page = url_response.read()
            _page = utils.convert_charset(_page)

            self.exist_set.add(self.url)
            logging.info("Get url:%s success." % self.url.url)

            return _page

        except Exception as err:
            logging.error(">>>>Get url:%s failed. Put it into failed_url_set" % self.url.url)
            self.exist_set.add(self.url)
            raise Exception(err)

    def parse_page(self, page):
        """
        Parse url from html page.

        Raises:
            Exception: An error occurred failing in parsing html page
        """
        try:
            html_parser = objects.PageParser(self.url, page)
            urls = html_parser.parse()      # List of Url object

            logging.info("Parse page of url:%s" % self.url.url)
            for url in urls:
                # if url not in exist_url_set:
                if url not in self.exist_set:
                    if url.depth <= self.configs['max_depth']:
                        self.url_queue.put(url, block=False)

        except Exception as err:
            raise Exception("Parse_page failed.\nError info:%s" % err)
        
    def save_page(self, page, save_path):
        """
        Save page to file, if url matches target_url pattern

        Raises:
            Exception: An error occurred failing in saving page to file
        """
        try:
            logging.info("Match target_url, saving page of url:%s" % self.url.url)
            save_filename = utils.url_to_filename(self.url.url)
            save_filepath = os.path.join(save_path, save_filename)
            with open(save_filepath, 'w') as fin:
                fin.write(page)

        except Exception as err:
            raise Exception("Save_page failed.\n%s" % err)
            

def mini_spider(args):
    """
    Mini-spider main function
    """
    try:
        configs = utils.check_config(args)
    except Exception as err:
        logging.error(err)
        logging.info("Mini-spider Exit!")
        return 

    thread_num = configs['thread_count']

    url_queue = Queue.Queue()   # queue of urls that waiting to be crawled 
    
    """Add seed url to url_queue"""
    with open(configs['url_list_file'], 'r') as fin:
        for line in fin.readlines():
            url = line.strip()
            url_queue.put(objects.Url(url, 0), block=False)

    """Start-up Spider process"""
    logging.info("Mini-spider process Begin!")

    spider_manager = SpiderManager(url_queue, thread_num, configs)
    spider_manager.wait_all_complete()
    
    logging.info("Mini-spider process Done!")

if __name__ == "__main__":
    """Logging config"""
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s', 
                        filename='log.mini-spider', filemode='w')

    parser = argparse.ArgumentParser(description=__doc__,
                                    formatter_class=argparse.RawTextHelpFormatter)

    _help = 'Show version of mini-spider'
    parser.add_argument('-v', '--version', action="version",
                                           help=_help,
                                           version='Version:%s' % VERSION)
    _help = "Config file url for mini-spider"
    parser.add_argument('-c', '--config', help=_help)

    args = parser.parse_args()
    mini_spider(args)
