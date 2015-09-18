#coding=utf8
import os,sys
from bs3 import BeautifulSoup

class HtmlParser(object):
	def __init__(self,html):
		self.html = html

