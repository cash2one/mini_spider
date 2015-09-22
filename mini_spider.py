#coding=utf8
import os,sys
import argparse
from argparse import RawTextHelpFormatter
import ConfigParser
import threading
import logging
import Queue
import urllib2, time
from objects import Url, HtmlParser
from utils import check_config, convert_charset, url_to_filename

url_queue = Queue.Queue()
exist_url_set = set()
failed_url_set = set()

class SpiderManager(object):
	def __init__(self, thread_num = 4, configs=None):
		self.threads = []
		self.configs = configs
		self.__init_thread_pool(thread_num)
	
	def __init_thread_pool(self, thread_num):
		global url_queue
		for i in range(thread_num):
			self.threads.append(SpiderThread(i, url_queue, self.configs))
	
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
		self.configs = configs
		self.idx = thread_idx
		self.start()	#Start thread

	def run(self):
		"""Rewrite run function"""
		retry = 3
		while retry:
			try:
				"""Doing job"""
				logging.info("Thread %s getting job url from work_queue"%(self.idx))
				logging.debug("Thread:%s, queue_size:%s"%(self.idx,url_queue.qsize()))
				url = self._queue.get(block=True, timeout=10)

				"""Crawl page from website"""
				spider = Spider(url, self.configs)
				spider.do_all_jobs()

				"""Notificate queue when job done"""
				self._queue.task_done()

			except Exception,e:
				sleep_time = 5
				logging.info("Thread %s get job failed, retry times left: %s, sleep %s seconds and retry.\n%s"%(self.idx, retry, sleep_time, e))
				retry -= 1
				time.sleep(sleep_time)

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

	def do_all_jobs(self):
		try:
			self.get_page()
			self.parse_page()
			self.save_page()
		except Exception, e:
			logging.error("Getting page failed, url:%s\n%s"%(self.url.url,e))
		#self.clean_up()

	def get_page(self):
		'''
		Get html file from Internet
		'''
		_timeout = self.configs['crawl_timeout']

		try:
			url_respone = urllib2.urlopen(self.url.url, timeout=_timeout)
			_page = url_respone.read()
			self.page = convert_charset(_page)
			global exist_url_set
			exist_url_set.add(self.url)
			logging.info("Get url:%s success."%(self.url.url))
		except Exception, e:
			global failed_url_set
			failed_url_set.add(self.url)
			raise Exception(e)

	def parse_page(self):
		global url_queue
		global exist_url_set
		global failed_url_set
		
		"""Get """
		try:
			html_parser = HtmlParser(self.url, self.page, self.configs)
			urls = html_parser.parse()		#List of Url object

			logging.info("Parse page of url:%s"%(self.url.url))
			for url in urls:
				if not url in exist_url_set and not url in failed_url_set:
					if url.depth <= self.configs['max_depth']:
						url_queue.put(url,block=False)
			logging.debug("queue_size:%s"%(url_queue.qsize()))
		except Exception,e:
			raise Exception("Parse_page failed.\n%s"%(e))
		
	def save_page(self):
		try:
			save_path = self.configs['output_dir']
			save_filename = url_to_filename(self.url.url)
			save_filepath= os.path.join(save_path,save_filename)
			logging.info("Save page of url:%s"%(self.url.url))
			with open(save_filepath,'w') as fin:
				fin.write(self.page)

		except Exception, e:
			raise Exception("Save_page failed.\n%s"%(e))
			

def main(args):
	configs = check_config(args)
	thread_num = configs['thread_count']
	
	#Add seed url to url_queue
	global url_queue
	with open(configs['url_list_file'],'r') as fin:
		for line in fin.readlines():
			url = line.strip()
			url_queue.put(Url(url,0),block=False)

	"""For spider test"""
	'''
	spider = Spider(url_queue.get(block=True),configs)
	spider.get_page()
	spider.parse_page()
	spider.save_page()
	'''
	
	"""Main Spider process"""
	logging.info("Mini-spider process Begin!")

	spider_manager = SpiderManager(thread_num, configs)
	spider_manager.wait_all_complete()
	
	logging.info("Mini-spider process Done!")

if __name__=="__main__":
	'''Logging config'''
	logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')

	parser = argparse.ArgumentParser(description=__doc__, 
				formatter_class=RawTextHelpFormatter)
	parser.add_argument('-c','--config', help="Config file url for mini-spider")
	args = parser.parse_args()
	main(args)
