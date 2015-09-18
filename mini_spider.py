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
from tools import check_config

url_queue = list()
exist_url_queue = set()

class SpiderManager(object):
	def __init__(self, thread_num = 4):
		self.work_queue = Queue.queue()
		self.threads = []
		self.
	
	def __init_thread_pool(self, thread_num):
		for i in range(thread_num):
			self.threads.append(Spider(self.work_queue))
	
	def __init_work_queue(self, jobs_num):
		pass

	def add_job(self):
		pass

class Spider(threading.Thread):
	def __init__(self, work_queue):
		threading.Thread.__init__(self)
		self._queue = work_queue
	def run(self):
		pass

def main(args):
	check_config(args)
	
if __name__=="__main__":
	'''Logging config'''
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')

	parser = argparse.ArgumentParser(description=__doc__, 
				formatter_class=RawTextHelpFormatter)
	parser.add_argument('-c','--config', help="Config file url for mini-spider")
	args = parser.parse_args()
	main(args)
