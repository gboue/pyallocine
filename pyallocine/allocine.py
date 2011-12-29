#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
	allocine.py allows searching for movies on allocine and retrieving
	information about a particular movie
	
	http://regexpal.com/ used for testing regexp
	
	It mainly parses the allocine website
	
	Usage:
		allocine.py -t "movie_title"
		allocine.py -t "movie_title" --lucky
		allocine.py --id allocine_id
	
	Colophon:
	
		urllib
		re 
		optparse for the command line
	
		Inspired from ruby version 
			http://github.com/webs/allocine
	
	Author: Guillaume BOUÉ
	Creation Date : 2010-01-16
	Version: 1
"""

from optparse import OptionParser
import sys, os, re, random
import urllib, urllib2, time, base64
import xml.dom.minidom
import locale
import logging

# VAR AND CONSTANTS 
# =================


# URLS

MOVIE_SEARCH_URL = "http://www.allocine.fr/recherche/1/?q=%s"
MOVIE_DETAIL_URL = "http://www.allocine.fr/film/fichefilm_gen_cfilm=%s.html"
SHOW_SEARCH_URL = "http://www.allocine.fr/recherche/?motcle=%s&rub=6"
SHOW_DETAIL_URL = "http://www.allocine.fr/series/ficheserie_gen_c	serie=%s.html"

# REGULAR EXPRESSIONS

FIND_MOVIE_REGEXP = """<img.*?src='(.*?)'.*?alt='.*?' /></a>.*?</td><td style=" vertical-align:top;" class="totalwidth"><div><div style="margin-top:-5px;">\s*<a href='\/film\/fichefilm_gen_cfilm=(\d+).html'>(.*?)<\/a>.*?<span class="fs11">(.*?)</span>"""
FIND_INFO_MOVIE_REGEXP ={
	'date' : '^ (\d{4}) ',
	'director': "de (.*?)(avec|$)",
	'actors': "avec(.*)",
}


MOVIE_REGEXPS = {
  'title' : u'<h1.*?>(.*?)<\/h1>',
  'directors' : u'R.*? par<\/span>(?:.*?)<div class="oflow_a">(.*?)<\/li>',
  'nat' : u'Nationalit.*?<\/span>(.*?)<\/li>',
  'genres' : u'Genre<\/span>(.*?)<\/li>',
  'out_date' : u'itemprop="datePublished" content="(.*?)"',
  'duree' : u"""itemprop="duration"(?:.*?)>(.*?)</span>""",
  'production_date' : u'Ann.*?e de production :(.*?)</a>',
  'original_title' : u'<th>Titre original</th><td>(.*?)<\/td>',
  'actors' : u'Avec.*?<\/span>(.*?)<\/li>',
  'synopsis' : u'<p itemprop="description">(.*?)</p>',
  'image' : u"""<link rel="image_src" href="(.*?)" />""",
  'interdit' : u'<span class="insist">(Interdit.*?)</span>'
}


import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
      keep &amp;, &gt;, &lt; in the source code.
   from Fredrik Lundh
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            print "erreur de valeur"
            pass
      else:
         # named entity
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               print text[1:-1]
               text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
         except KeyError:
            print "keyerror"
            pass
      return text # leave as is

   res = ""
   try:
      text = text.decode('utf-8')
      res = re.sub("&#?\w+;", fixup, text)
      res = res.encode('utf-8')
   except:
	  res = re.sub("&#?\w+;", fixup, text)

   return res

# MAIN CLASS
# ==========

class Movie:
  	
	title = ""
	directors =""
	nat = ""
	genres = ""
	out_date = None
	duree = ""
	production_date = ""
	original_title = ""
	actors = ""
	synopsis = ""
	image = ""
	interdit = None

	def __init__(self, id, debug=True):
		
		data = Movie.get_url_data(MOVIE_DETAIL_URL % id)
		
		for regxp_id, regxp in MOVIE_REGEXPS.iteritems():
			
			if debug: 
				logging.debug("%s : %s" % (regxp_id, regxp ))
				pass
				
			r = re.compile(regxp, re.DOTALL | re.MULTILINE | re.UNICODE)
			str = re.search(r, data)
			if str:
				d = re.sub('<(.+?)>','', str.group(1).strip())
				d  = re.sub('\r\n','', d)
				d  = re.sub('\r','', d)
				d  = re.sub('\n','', d)
				d  = re.sub('[ ]+',' ', d)
				d  = re.sub('\s\s+',' ', d)

				# special treatment for plus of actors
				d  = re.sub('plusplus$','#£', d)
				d  = re.sub('plus$','', d)
				d  = re.sub('#£$','plus', d)
				d  = re.sub(',$','', d)
				d  = unescape(d)
				self.__dict__[regxp_id] = d
				# d.encode('utf-8')
				
				#print "       %s " % d
			
			
	@classmethod
  	def find(self, search):
		# 1. Clean the search string
		#search = search.replace(' ', '+')
		#search = search.decode('utf-8').encode('iso-8859-1')
		search = urllib.quote_plus(search)
		logging.info(search)
    
		# 2. Get raw data from allocine
 		data = Movie.get_url_data(MOVIE_SEARCH_URL % search)
		
		# 3. Get 
		matchList = re.findall(FIND_MOVIE_REGEXP, data, re.DOTALL | re.MULTILINE)
		
		movies = {}
		for (img,id, name,info) in matchList:
			#print info
			name  = re.sub('<(.+?)>','', name)
			name  = re.sub('\r\n','', name)
			#movies[id]=name.strip()
			
			movies[id]={'image':img,'name' : name.strip()}
			
			info = re.sub('<br>','###', info)
			info = re.sub('<(.+?)>','', info)
			info = re.sub('\r\n','', info)
			info = re.sub('\t','', info)
			info = re.sub('\s+',' ', info)
			
			logging.info(info)
			for regxp_id, regxp in FIND_INFO_MOVIE_REGEXP.iteritems():

				r = re.compile(regxp, re.DOTALL | re.MULTILINE | re.UNICODE)
				str = re.search(r, info)
				if str:
					d = re.sub('<(.+?)>','', str.group(1).strip())
					d  = re.sub('\r\n','', d)
					d  = re.sub('[ ]+',' ', d)
					d  = re.sub('\s\s+',' ', d)
					d = unescape(d)
					movies[id][regxp_id] = d
			
			logging.info(movies[id])
			
			#str = re.search(r_info, info)
			#if str:
			#	movies[id]={'image':img,'name' : name.strip(), 'date' : str.group(1).strip(),\
			#	'director' : str.group(2).strip(),'actors' : str.group(3).strip() }
			#else:
			#	movies[id]={'image':img, 'name' : name.strip(), 'info' : info}
			
		return movies	
	#end find
  
	@classmethod
	def get_url_data(self, url):
		"""
		Get url data fetches all the data from an url
		utf-8 conversion is applied
		"""
		
		logging.info(url)

		# 1. Get info and data regarding that url
		u = urllib2.urlopen(url)
		data = u.read()
		info = u.info()
		u.close()

		#import pdb
		#pdb.set_trace()

		# 2. utf8 conversion
		charset = "utf-8"    
		ignore, charset = info['Content-Type'].split('charset=')
		data = data.decode(charset)
		#.encode('utf-8')  

		logging.debug(data)

		return data

	@classmethod
  	def lucky_find(self, search):
		"""
		Return the first movie 
		"""
		results = Movie.find(search)
		if results and len(results) > 0 :
			
			m = Movie(results.keys()[0]) 
			return m
			
	#end lucky_find
  
  	def __str__(self):
		"""
		String representation of a movie
		"""
		return "%s ; %s ; %s ; %s ; %s ; %s ; %s ; %s ; %s ; %s ; %s ; %s " % \
												(self.title, self.directors,self.nat, self.genres, \
												self.out_date,self.duree, self.production_date, \
												self.original_title, self.synopsis,self.image, \
												self.interdit , self.actors )

# MAIN 
# =====	


def print_movie(movie):
	"""
	Print attributes of a movie object
	"""
	for x,y in movie.__dict__.items():
		print "%20s ==> %s" % (x, y,)

def print_movie_list(movies):
	"""
	Print a tabular representation of the movie result list
	"""
	for movie_id, movie_info in movies.iteritems():
		try:
			# 1. Get optional info
			infos = []
			for attr in ['director','date','actors','info']:
				if movie_info.has_key(attr):
					infos.append(movie_info[attr])
				else:
					infos.append("")
			
			# 2. print tabular result
			print "%10s / %50s ==> %-20s %5s %20s %30s %s" % (movie_id,movie_info['name'], infos[0][:20], infos[1],  infos[2][:20] , infos[3][:30], movie_info['image'])
		except:
			print movie_id

def main():
	
	usage = "usage: %prog [options] "
	parser = OptionParser(usage=usage)
	parser.add_option("-t", "--title", dest="movie_title", help='Search for this movie')
	parser.add_option("-i", "--id",  dest="movie_id", help='Get info from this movie')
	parser.add_option("--lucky",  dest="lucky", help='Get info from the first movie found.\n Movie title must be indicated', action="store_true")
	(options, args) = parser.parse_args()
	
	# 1. Search from a movie title
	if options.movie_title:
		
		if options.lucky:
			movie = Movie.lucky_find(options.movie_title)
			print_movie(movie)
		else:	
			movies = Movie.find(options.movie_title)
			print_movie_list(movies)
	
	# 2. Or a movie id
	elif options.movie_id:	

		movie = Movie(options.movie_id)
		print_movie(movie)
	
	else:
		parser.error("Bad usage")

logging.basicConfig(
    level = logging.ERROR,
    format = '[%(asctime)s] %(levelname)s %(message)s',	
)

if __name__ == '__main__':
	main()
    
