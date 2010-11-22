#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import urllib, urllib2
import logging
import re

CINE35_URL="http://cine35.com/"

FIND_MOVIE_REGEXP = """<form method="GET" action="Film.asp">(.*?)</form>"""
MOVIE_INFO_REGEXP = """<option value="(.*?)">(.*?)</option>"""

MOVIE_DETAIL_URL = "http://www.cine35.com/Film.asp?Code=%s"

def get_url_data(url):
	
	u = urllib2.urlopen(url)
	data = u.read()
	info = u.info()
	u.close()

	data = data.decode("cp1252").encode('utf-8')  

	return data
	
def get_all_movie():
	
	# 2. Get raw data from allocine
	data = get_url_data(CINE35_URL)
	
	# 3. Get 
	match_form = re.search(FIND_MOVIE_REGEXP, data, re.DOTALL | re.MULTILINE )
	movies_data = match_form.group(0)
	
	match_list = re.findall(MOVIE_INFO_REGEXP, movies_data, re.DOTALL | re.MULTILINE | re.I)

	
	return match_list

def search_movie(movie_title):
	
	movie_list = get_all_movie()
	lower_movie_title=movie_title.lower()
	return [(x,y) for  x, y in movie_list if y.lower().find(lower_movie_title) >= 0]

	
def main():

	l = search_movie(sys.argv[1])
	#l = get_all_movie()
	print l

if __name__ == '__main__':
	main()