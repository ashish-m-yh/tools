import re
import string
import json

from subprocess import check_output

from nltk import pos_tag, word_tokenize, clean_html
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import names

from httplib2 import Http

import requests
from bs4 import BeautifulSoup

class StreamParser:
	def __init__(self):
		self._senti = None

	def set_text(self,txt):
		self._input  = clean_html(txt)

		self._fields = dict()
		self._ltokens = set() 
		self._tokens = [] 
		self._tags   = []
		
		if self._input is not None and len(self._input) > 0:
			lem = WordNetLemmatizer() 

			for x in word_tokenize(self._input):
				self._ltokens.add(lem.lemmatize(x.translate(string.maketrans("",""), string.punctuation).lower()))
				self._tokens.append(x)

	def set_source(self,fname,ftype):
		st = ''
		if ftype == 'application/msword':
			try:
				st = check_output(["antiword",fname])
			except:
				pass
		elif ftype == 'application/pdf':
			try:
				st = check_output(["pdftotext",fname,"-"])
			except:
				pass
		else:
			fo = open (fname,"r")
			st = fo.read()
			fo.close()

		self.set_text(st)

	def get_fields(self):
		self._fields['email'] = self.extract_email()
		self._fields['url']   = self.extract_url()
		self._fields['tel']   = self.extract_tel()

		return self._fields

	def raw_text(self):
		return self._input

	def get_ltokens(self):
		return self._ltokens

	def get_tokens(self):
		return self._tokens

	def extract_tel(self):
		mystr = re.sub(r'\D\d{4}\-\d{2}\-\d{2}\D','',self._input)
		mystr = re.sub(r'\D\d{2}\-\d{2}\-\d{4}\D','',mystr)
		mystr = re.sub(r'(\d+:)+','',re.sub(r'(\d)\s',r"\1",re.sub(r'\-','',mystr)))
		mystr = re.sub(r"\b(?i)hi|(?i)hello|(?i)dear\b",'',mystr)
		mystr = re.sub(r"\b(?i)[a-z]+[\,\b]",'',mystr,1)

		m = re.findall('[\s\-:]\+?(\d{5,})+\D?',mystr) 

		tel_list  = dict() 
		prevnames = []
 
		if m is not None:
		#	allnames = names.words()
			for i in m:
				regex   = r'(.*?)'+re.escape(i)
				tmp_arr = re.findall(regex,mystr,re.MULTILINE)
				tmpstr  = re.sub(regex,'',mystr)

				if tmpstr is not None:
					mystr = tmpstr

				if len(tmp_arr) > 0:
					tmplist = self._detect_names(tmp_arr[0])

					if len(tmplist) == 0:
						tel_list[i.rstrip()] = prevnames												
					else:
						tel_list[i.rstrip()] = tmplist
						prevnames = tmplist

		return tel_list

	def _detect_names(self,substr):
		allnames = names.words()
		namelist = set()
		nounlist = set()
		
		words = word_tokenize(substr)

		for n in xrange(len(words)):
			if words[n] in allnames or self.name_finder(words[n]) == True:
				tmplist = [ words[n] ]
				delim   = ' '

				for x in xrange(1,4):
					n += x
					if n < len(words):
						if words[n] in allnames or re.match('^[A-Z]$',words[n]):
							tmplist.append(words[n])
							nounlist.add(words[n])	

				namelist.add(delim.join(tmplist))

		return list(namelist-nounlist)
		
	def name_finder(self,name):
		url = "http://search.yahoo.com/search?p=%s"
		query = name + " site: babycenter.com"
		r = requests.get(url % query) 

		soup = BeautifulSoup(r.text)
		soup.find_all(attrs={"class": "yschttl"})

		is_name = False

		for link in soup.find_all(attrs={"class": "yschttl"}):
			myurl = link.get('href')

			if re.search('baby-names',myurl) is not None:
				is_name = True	
				break 

		return is_name
		
	def extract_email(self):
		m 	   = re.findall('([\w\.-]+@[\w\.-]+\.\w+)',self._input,re.IGNORECASE)
		emails = []
	
		for i in m:
			if i not in emails:
				emails.append(i)

		return emails

	def extract_pincode(self):
		mystr = re.sub(r'\D\d{4}\-\d{2}\-\d{2}\D','',self._input)
		mystr = re.sub(r'\D\d{2}\-\d{2}\-\d{4}\D','',mystr)
		mystr = re.sub(r'(\d+:)+','',re.sub(r'(\d)\s',r"\1",re.sub(r'\-','',mystr)))
		m	  = re.findall("\\b\d{4,6}\\b", mystr)

		pins  = []

		for i in m:
			if i not in pins:
				pins.append(i)

		return pins

	def extract_url(self):
		pats = [ '(https?://\S+)', '(www\.\S+)' ]
		urls = []

		for p in pats:
			m = re.findall(p,self._input,re.IGNORECASE)
			for i in m:
				i = re.sub(r'https?://','',i)
				if i not in urls:
					urls.append(i)

		return urls

"""
	def get_tags(self):
		inp = re.sub("\n\n","\n",self._input)
		inp = re.sub("\s+"," ",inp)
			
		tags = []

		try:	
			tagger = nerclient.NERClient()
			tags   = tagger.tag_text(inp)
		except:
			pass

		return tags
"""
