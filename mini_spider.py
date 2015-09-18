#coding=utf8
import os,sys
import argparse
from argparse import RawTextHelpFormatter
import ConfigParser
import threading
import logging
import Queue
import urllib2
from objects import Url
from utils import check_config

class SpiderManager(object):
	def __init__(self, thread_num = 4, configs=None):
		self.threads = []
		self.__init_thread_pool(thread_num)

	def __init_thread_pool(self, thread_num):
		for i in range(thread_num):
			self.threads.append(SpiderThread())
	
	def add_job(self):
		pass

class SpiderThread(threading.Thread):
	def __init__(self, work_queue):
		super(Thread,self).__init__()	#调用父类的构造函数
		self._queue = work_queue
	def run(self):
		pass

class Spider(object):
	'''
	Main spider process
	'''
	def __init__(self, url, configs):
		'''
		Initiate
		@params[in] url: objects.Url
		@params[in] timeout : int, timeout for getting page
		'''
		self.url = url
		self.configs = configs

	def crawl(self):
		self.get_page()
		self.parse_page()
		self.save_page()
		self.clean_up()

	def get_page(self):
		'''
		Get html file from Internet
		'''
		_timeout = self.configs['crawl_timeout']

		try:
			self.page = urllib2.urlopen(self.url.url,timeout=_timeout).read()
			global exist_url_set
			exist_url_set.add(self.url)
			logging.info("Get url:%s success."%(self.url.url))
		except :
			global failed_url_set
			failed_url_set.add(self.url)
			logging.info("Get url:%s failed."%(self.url.url))


	def parse_page(self):
		global exist_url_set
		global failed_url_set
		global url_queue

		html_parser = HtmlParser(self.page,self.url.depth)
		urls = html_parser.parse()		#List of Url object

		for url in urls:
			if not url in exist_url_set and not url in failed_url_set:
				url_queue.put(url)

	def save_page(self):
		pass


url_queue = Queue.Queue()
exist_url_set = set()
failed_url_set = set()

def main(args):
	configs = check_config(args)
	thread_num = configs['thread_count']
	
	#Add seed url to url_queue
	global url_queue
	with open(configs['url_list_file'],'r') as fin:
		for line in fin.readlines():
			url = line.strip()
			url_queue.put(Url(url,0),block=True)
	
	spider = Spider(url_queue.get(block=True),configs)
	spider.get_page()
	print spider.page
	#spider_manager = SpiderManager(thread_num, configs)

if __name__=="__main__":
	'''Logging config'''
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')

	parser = argparse.ArgumentParser(description=__doc__, 
				formatter_class=RawTextHelpFormatter)
	parser.add_argument('-c','--config', help="Config file url for mini-spider")
	args = parser.parse_args()
	main(args)
