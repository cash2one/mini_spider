#coding=utf8
import os,sys
import re, chardet
import ConfigParser
import logging

def check_config(args):
	'''
	Used to check whether config setting is correct
	'''
	config_parser = ConfigParser.ConfigParser()
	config_parser.read(args.config)

	url_list_file = config_parser.get('spider','url_list_file')
	output_dir = config_parser.get('spider','output_directory')
	max_depth = config_parser.get('spider','max_depth')
	crawl_interval = config_parser.get('spider','crawl_interval')
	crawl_timeout = config_parser.get('spider','crawl_timeout')
	target_url = config_parser.get('spider','target_url')
	thread_count = config_parser.get('spider','thread_count')

	"""Set config"""
	config = {}

	'''Check url seed file'''
	if not os.path.isfile(url_list_file):
		raise IOError("Url_list_file : %s should be a file, please check!"%(url_list_file))
	else:
		config['url_list_file'] = url_list_file

	'''Check output dir'''
	if not os.path.isdir(output_dir):
		raise IOError("Output directory : %s should be a directory, please check!"%(output_dir))
	else:
		config['output_dir'] = output_dir

	'''Check max_depth'''
	try:
		config['max_depth'] = int(max_depth)
	except:
		raise TypeError("Max_depth should be Integer type.")

	'''Check crawl_interval'''
	try:
		config['crawl_interval'] = int(crawl_interval)
	except:
		raise TypeError("Crawl_interval should be Integer type.")

	'''Check crawl_timeout'''
	try:
		config['crawl_timeout'] = int(crawl_timeout)
	except:
		raise TypeError("Crawl_timeout should be Integer type.")
	
	'''Check target_url'''
	try:
		re.compile(target_url)
		config['target_url']=target_url
	except:
		raise Exception("Target_url should be a Regular Expression.")

	'''Check thread_count'''
	try:
		config['thread_count'] = int(thread_count)
	except:
		raise TypeError("Tread_count should be Integer type.")

	return config

def convert_charset(html):
	charset = chardet.detect(html)['encoding']
	print charset
	if charset == 'utf-8':
		return html
	elif charset.startswith('GB') or charset.startswith('gb'):
		_html = html.decode('gbk')
		_html = _html.encode('utf-8')
		return _html
		
