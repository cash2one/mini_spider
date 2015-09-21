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
from utils import check_config, convert_charset

url_queue = Queue.Queue()
exist_url_set = set()
failed_url_set = set()

class SpiderManager(object):
	def __init__(self, thread_num = 4, configs=None):
		self.threads = []
		self.__init_thread_pool(thread_num)

	def __init_thread_pool(self, thread_num):
		for i in range(thread_num):
			self.threads.append(SpiderThread(i, job_queue, configs))
	
	def wait_all_complete(self):
		for spider in self.threads:
			if spider.isAlive():
				spider.join()

class SpiderThread(threading.Thread):
	"""
	SpiderThread
	"""
	def __init__(self, thread_idx ,work_queue, configs):
		"""
		Initiate
		@param [in] thread_idx: index of thread
		@param [in] work_queue: url queue for crawling, for synchronize
		@param [in] configs: configuration, dict
		"""
		threading.Thread.__init__(self)	#call init func of Thread class
		self._queue = work_queue
		self.idx = thread_idx
		self.start()	#Start thread

	def run(self):
		"""Rewrite run function"""
		retry = 5
		while retry:
			try:
				"""Doing job"""
				logging.info("Thread %s getting job url from work_queue"%(self.idx))
				url = self._queue.get(block=True, timeout=10)

				"""Crawl page from website"""
				
				"""Notificate queue when job done"""
				self._queue.task_done()

			except:
				sleep_time = 10
				logging.info("Thread %s get job failed, retry times left: %s, sleep %s seconds and retry."%(self.idx, retry, sleep_time))
				retry -= 1
				time.sleep(sleep_time)

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
