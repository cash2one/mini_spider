#coding=utf8
import os, sys

class Url(object):
	def __init__(self, url, depth):
		self.url = url
		self.depth = depth
	
	def __eq__(self, other):
		return self.url == other.url

