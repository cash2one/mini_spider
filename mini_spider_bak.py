#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides main entrance of mini-spider with multi-thread.

Author: linzebin(linzebin@baidu.com)

Date: 2015/9/26

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
from argparse import RawTextHelpFormatter

import Queue

from objects import Url
from objects import HtmlParser
from utils import check_config
from utils import convert_charset
from utils import url_to_filename


VERSION=1.0

url_queue = Queue.Queue()   # queue of urls that waiting to be crawled 
exist_url_set = set()       # set of urls which are crawled
failed_url_set = set()      # set of urls which are get failed


class SpiderManager(object):
    """
    WorkManager 
    """
    def __init__(self, thread_num=4, configs=None):
        """Init WorkManager with thread_num and configuration"""
        self.threads = []
        self.configs = configs
        self.__init_thread_pool(thread_num)
    
    def __init_thread_pool(self, thread_num):
        """Init thread pool with thread_num to 
            limit the number of SpiderThread"""
        global url_queue
        for i in range(thread_num):
            self.threads.append(SpiderThread(i, url_queue, self.configs))
    
    def wait_all_complete(self):
        """Check whether all SpiderThread is alive"""
        for spider in self.threads:
            if spider.isAlive():
                spider.join()


class SpiderThread(threading.Thread):
    """
    SpiderThread class to execute Spider-process
    """
    def __init__(self, thread_idx, work_queue, configs):
        """
        Init SpiderThread with thread_idx, work_queue and configs

        @param [in] thread_idx: index of thread
        @param [in] work_queue: url queue for crawling, for synchronize
        @param [in] configs: configuration, dict
        """
        threading.Thread.__init__(self)  # Call init func of Thread class
        self._queue = work_queue
        self.configs = configs
        self.idx = thread_idx
        self.start()  # Start thread

    def run(self):
        """Overwrite run function of threading.Thread"""
        retry = 2
        while retry:
            try:
                """Doing job"""
                logging.info("Thread %s getting job url from work_queue" % self.idx)
                url = self._queue.get(block=True, timeout=5)

                """Crawl page from website"""
                spider = Spider(url, self.configs)
                spider.do_all_jobs()

                """Notify queue when job done"""
                self._queue.task_done()

            except Exception as err:
                sleep_time = 3
                log_info = "Thread %s get job failed, retry times left:%s,\
                            sleep %s seconds and retry.\n ERROR:%s"
                logging.info(log_info % (self.idx, retry, sleep_time, err))
                retry -= 1
                time.sleep(sleep_time)


class Spider(object):
    """
    Main spider process

    Attribute:
        url : basic url info, objects.Url. Containing url and depth 
        configs : a dictionary of configurations 
    """
    def __init__(self, url, configs):
        """
        Initiate spider
        @params[in] url: objects.Url
        @params[in] timeout : int, timeout for getting page
        """
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

            # Spider sleep
            time.sleep(crawl_interval)

        except Exception as err:
            logging.error("Getting page failed, url:%s\n%s" % (self.url.url, err))

    def get_page(self):
        """
        Get html page from Internet
        """
        _timeout = self.configs['crawl_timeout']

        try:
            url_response = urllib2.urlopen(self.url.url, timeout=_timeout)
            _page = url_response.read()
            _page = convert_charset(_page)

            global exist_url_set
            exist_url_set.add(self.url)
            logging.info("Get url:%s success." % self.url.url)

            return _page

        except Exception as err:
            global failed_url_set
            logging.error(">>>>Get url:%s failed. Put it into failed_url_set" % self.url.url)
            failed_url_set.add(self.url)
            logging.error(">>>>Failed_Set size:%s" % (len(failed_url_set)))
            raise Exception(err)

    def parse_page(self, page):
        """
        Parse url from html page.
        """
        global url_queue
        global exist_url_set
        global failed_url_set
        
        try:
            html_parser = HtmlParser(self.url, page)
            urls = html_parser.parse()      # List of Url object

            logging.info("Parse page of url:%s" % self.url.url)
            for url in urls:
                if url not in exist_url_set and url not in failed_url_set:
                    if url.depth <= self.configs['max_depth']:
                        url_queue.put(url, block=False)

        except Exception as err:
            raise Exception("Parse_page failed.\nError info:%s" % err)
        
    def save_page(self, page, save_path):
        """
        Save page to file, if url matches target_url pattern
        """
        try:
            logging.info("Match target_url, saving page of url:%s" % self.url.url)
            save_filename = url_to_filename(self.url.url)
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
        configs = check_config(args)
    except Exception as err:
        logging.error(err)
        logging.info("Mini-spider Exit!")
        return 

    thread_num = configs['thread_count']
    
    """Add seed url to url_queue"""
    global url_queue
    with open(configs['url_list_file'], 'r') as fin:
        for line in fin.readlines():
            url = line.strip()
            url_queue.put(Url(url, 0), block=False)

    """Start-up Spider process"""
    logging.info("Mini-spider process Begin!")

    spider_manager = SpiderManager(thread_num, configs)
    spider_manager.wait_all_complete()
    
    logging.info("Mini-spider process Done!")

if __name__ == "__main__":
    """Logging config"""
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s', 
                        filename='log.mini-spider', filemode='w')

    parser = argparse.ArgumentParser(description=__doc__,
                                    formatter_class=RawTextHelpFormatter)

    _help = 'Show version of mini-spider'
    parser.add_argument('-v', '--version', action="version",
                                           help=_help,
                                           version='Version:%s' % VERSION)
    _help = "Config file url for mini-spider"
    parser.add_argument('-c', '--config', help=_help)

    args = parser.parse_args()
    mini_spider(args)
