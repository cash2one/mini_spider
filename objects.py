#coding=utf8
import os, sys
import re
from bs4 import BeautifulSoup

class Url(object):
	def __init__(self, url, depth):
		self.url = url
		self.depth = depth
	
	def __eq__(self, other):
		return self.url == other.url

class HtmlParser(object):
	def __init__(self, url, html, configs):
		'''
		@params[in] url: object.Url
		@params[in] html: page content
		@params[in] cofnigs: configuration
		'''
		self.html = html
		self.url = url
		self.root_url = '/'.join(url.url.split('/')[:3])
		self.configs = configs
		
	def parse(self):
		url_queue = []
		soup = BeautifulSoup(self.html,'html.parser')
		links = soup.find_all('a')

		'''Todo: url extract logic is not right'''
		for link in links:
			sub_url = link.get('href')
			if sub_url.startswith('http'):
				link_url = sub_url
			elif not 'javascript' in sub_url:
				link_url = self.root_url+'/'+sub_url
				'''
				if sub_url.startswith('/'):
					link_url = self.root_url+'/'+sub_url
				else:
					link_url = '/'.join(self.url.url.split('/')[:-1])+'/'+sub_url
				'''
			else:
				re_url = re.compile('href=\"([\s\S]*.html)\"')
				sub_url = re_url.findall(sub_url)[0]
				link_url = self.root_url+'/'+sub_url
			url_queue.append(Url(link_url,self.url.depth+1))
		return url_queue

