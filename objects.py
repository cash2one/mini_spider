#coding=utf8
import os, sys
from bs3 import BeautifulSoup

class Url(object):
	def __init__(self, url, depth):
		self.url = url
		self.depth = depth
	
	def __eq__(self, other):
		return self.url == other.url

class HtmlParser(object):
	def __init__(self, html, depth, configs):
		pass
	
	def parse(self):
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

	def do_all_jobs(self):
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
			url_respone = urllib2.urlopen(self.url.url, timeout=_timeout)
			_page = url_respone.read()
			self.page = convert_charset(_page)
			global exist_url_set
			exist_url_set.add(self.url)
			logging.info("Get url:%s success."%(self.url.url))
		except Exception, e:
			global failed_url_set
			failed_url_set.add(self.url)
			logging.error("Get url:%s failed."%(self.url.url))
			logging.error(e)

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
