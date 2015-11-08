#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provided neccessary objects to mini-spider

Author: linzebin (linzebin@badiu.com)
Date: 2015/9/27
"""
import re
import logging

from bs4 import BeautifulSoup


class Url(object):
    """
    class to store url and depth

    Attributes:
        url : A string, url of website
        depth : An integer, represent the depth from seed url
    """
    def __init__(self, url, depth):
        """Inits Url object with url and depth"""
        self.url = url
        self.depth = depth
    
    def __eq__(self, other):
        """Over-write __eq__"""
        return self.url == other.url

    def __hash__(self):
        """Over-write __hash__"""
        return hash(self.url)


class PageParser(object):
    """
    Class to parse html page 

    Attributes:
        html : A string containing page of url
        url : A Url object
        root_url : A strint represent root path of url

    """
    def __init__(self, url, html):
        """
        Inits HtmlParser with url, html
        @params[in] html: page content
        """
        self.html = html
        self.url = url
        self.root_url = '/'.join(url.url.split('/')[:3])
        
    def parse(self):
        """
        Parse urls from html page
        
        Returns:
            url_queue : A list of urls extracted from html
        """
        url_queue = []
        soup = BeautifulSoup(self.html, 'html.parser')
        
        base_link = soup.find_all('base')
        if base_link:
            base_link = base_link[0].get('href')[0]
            if base_link.startswith('http://'):
                relative_root_url = base_link
            else:
                relative_root_url = '/'.join(self.url.url.split('/')[:-1]) + '/' + base_link
        else:
            relative_root_url = '/'.join(self.url.url.split('/')[:-1])
        
        links = soup.find_all('a')

        '''Todo: handle abstract-path, relative-path and javascript'''
        for link in links:
            sub_url = link.get('href')
            if not sub_url:
                continue
            link_url = None
            # Handling abstract path
            if sub_url.startswith('http://'):
                link_url = sub_url
            # Handling relative path
            elif 'javascript' not in sub_url:
                if sub_url.startswith('/'):
                    link_url = self.root_url + sub_url
                elif self.url.depth == 0:
                    link_url = self.root_url + '/' + sub_url
                else:
                    link_url = relative_root_url + '/' + sub_url
            # Handling Javascript
            else:
                re_url = re.compile('href=\"([\s\S]*.html)\"')
                try:
                    sub_url = re_url.findall(sub_url)[0]
                    link_url = self.root_url + '/' + sub_url
                except Exception as err:
                    logging.info("No legal url is found.")

            if link_url:
                url_queue.append(Url(link_url, self.url.depth + 1))

        return url_queue

