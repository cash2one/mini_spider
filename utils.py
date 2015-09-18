#coding=utf8
import os,sys
import re
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

	'''Check url seed file'''
	if not os.path.isfile(url_list_file):
		raise Exception("Url_list_file : %s doesn't exist, please check!"%(url_list_file))
	
	'''Check output dir'''
	if not os.path.isdir(output_dir):
		raise Exception("Output directory : %s doesn't exist, please check!"%(output_dir))

	'''Check max_depth'''
	try:
		max_depth = int(max_depth)
	except:
		raise Exception("Max_depth should be Integer type.")

	'''Check crawl_interval'''
	try:
		crawl_interval = int(crawl_interval)
	except:
		raise Exception("Crawl_interval should be Integer type.")

	'''Check crawl_timeout'''
	try:
		crawl_timeout = int(crawl_timeout)
	except:
		raise Exception("Crawl_timeout should be Integer type.")
	
	'''Check target_url'''
	try:
		re.compile(target_url)
	except:
		raise Exception("Target_url should be a Regular Expression.")

	
	'''Check thread_count'''
	try:
		thread_count = int(thread_count)
	except:
		raise Exception("Tread_count should be Integer type.")
	
	return config_parser


