#coding=utf8
import os
import sys
import re
import ConfigParser
import logging

import chardet

def check_config(args):
	'''
	Check whether config setting is correct

	Args:
		args : arguments of spider setting, 
	
	Returns:
		a dictionary of arguments.
		
		example:
			{'url_list_file': './url.seed',
			'output_dir': './output',
			'max_depth': 3,
			...
			}

	Raises:
		IOError: 
				An error occurred when the config file is missing, or
				some arguments are setting incorrect
		TypeError:
				An error occurred when some arguments set to incorrect
				data type.
					example: max_depth should be integer
	'''

	config_parser = ConfigParser.ConfigParser()
	if not os.path.isfile(args.config):
		raise IOError("File:%s doesn't exist, please check!"%(args.config))
	#Read configs form file
	config_parser.read(args.config)
	try:
		url_list_file = config_parser.get('spider','url_list_file')
		output_dir = config_parser.get('spider','output_directory')
		max_depth = config_parser.get('spider','max_depth')
		crawl_interval = config_parser.get('spider','crawl_interval')
		crawl_timeout = config_parser.get('spider','crawl_timeout')
		target_url = config_parser.get('spider','target_url')
		thread_count = config_parser.get('spider','thread_count')
	except Exception, e:
		raise IOError(e)

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
		raise TypeError("'max_depth' should be Integer type.")

	'''Check crawl_interval'''
	try:
		config['crawl_interval'] = int(crawl_interval)
	except:
		raise TypeError("'crawl_interval' should be Integer type.")

	'''Check crawl_timeout'''
	try:
		config['crawl_timeout'] = int(crawl_timeout)
	except:
		raise TypeError("'crawl_timeout' should be Integer type.")
	
	'''Check target_url'''
	try:
		re.compile(target_url)
		config['target_url']=target_url
	except:
		raise Exception("'target_url' should be a legal Regular Expression.")

	'''Check thread_count'''
	try:
		config['thread_count'] = int(thread_count)
	except:
		raise TypeError("tread_count should be Integer type.")

	return config

def convert_charset(html):
	"""
	Convert different encoded page to utf-8
	
	Args:
		html : html page

	Returns:
		html : converted to utf-8 encoding 
	"""
	charset = chardet.detect(html)['encoding']
	if charset.startswith('GB') or charset.startswith('gb'):
		_html = html.decode('gbk')
		_html = _html.encode('utf-8')
		return _html
	else:
		return html

def url_to_filename(url):
	"""
	convert url to a legal filename, replace some special character with
	other specific string

	Args:
		url : url of website page

	Returns:
		filaname : filepath to save html page
	"""
	filname = url.replace('%', '%25')
	filename = filename.replace('/','%2F')
	filename = filename.replace('+', '%2B')
	filename = filename.replace('?', '%3F')
	filename = filename.replace('#','%23')
	filename = filename.replace('&', '%26')
	filename = filename.replace('=', '%3D')
	return filename

