#!/usr/bin/python
"""
Spellchecker

running at http://www.w3.org/2002/01/spellchecker

Share and Enjoy. Open Source license:
Copyright (c) 2001-2005 W3C (MIT, ERCIM, Keio)
http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231
$Id: spellchecker,v 1.2 2005/01/10 09:39:32 dom Exp $
 branched from v 1.46
"""
import re
import os
import cgi
import sys
import string
import urllib
import urlparse
import popen2
from sgmllib import SGMLParser
from threading import Thread

customized_dico="/usr/local/share/aspell/w3c.dat"
languages = {"en":"English","fr":"French"}
url_list = {}
base_domain = ""

def format_option(a,b,c):
        if a:
                selected=""
                if a==c:
                        selected=" selected='selected'"
                return "<option value='%s'%s>%s</option>" % (a,selected,b)

def concat(a,b):
        return a+b


Page1 ="""Content-Type:text/html


<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" lang="en-US">
<head>
  %s
  <title>W3C Spell Checker %s</title>
  <link rel="stylesheet" href="http://www.w3.org/Stylesheets/base"/>
  <link rel="stylesheet" href="http://www.w3.org/2001/11/results"/>
  <style type="text/css">
   ul.suggestions { height:5em; overflow:auto; width:10em;}
   
  </style>
</head>

<body>
<p><a href="http://www.w3.org"><img src="http://www.w3.org/Icons/w3c_home" alt="W3C"/></a></p>

<h1>W3C Spell Checker %s</h1>

<h2>Status</h2>
<p>This tool allows you to check the spelling of a web page. It currently only supports English and French.</p>

<h2>Usage</h2>
<form action="/cgi-bin/spellchecker.py" method="get"><p><label>URI of the document to be checked:<input type="text" value="%s" name="uri"/></label><br />
<label>Language of the document: <select name="lang">%s</select><br />
<label>Presents possible corrections: <input type="checkbox" name="suggest"%s /></label><br />
Check recursively <input type="checkbox" name="is_recursive" value="1"><br/>
<input type="submit" value="Get results"/></p></form>
"""

Page2 = """
<h2>See also</h2>
<ul>
<li><a href="http://www.w3.org/2002/08/diction">the W3C stylistic checker</a></li>
<li><a href="http://www.w3.org/QA/Tools">the QA Toolbox</a></li>
</ul>

<h2>References</h2>
<ul>
<li><a href="http://aspell.sourceforge.net">Aspell</a> is used in the back-end</li>
<li>The front-end is coded in <a href="http://www.python.org">Python</a></li>
</ul>
<h2>Known bugs and limitations</h2>
<ul>
<li>Doesn't handle language switching on the <code>lang</code> and <code>xml:lang</code> attributes</li>
<li>Doesn't check textual attributes (e.g. <code>title</code>, <code>alt</code>)</li>
</ul>
<hr/>
<address><a href="http://www.w3.org/People/Dom/">Dominique Haza&euml;l-Massieux</a><br/>
Last Modified: $Date: 2005/01/10 09:39:32 $
</address>
</body>
</html>
"""

def format(fp,suggest):
	line = fp.readline()
	words = {}
	count = 0
	while line!="":
		if line!="\n" and line !="*\n" and line[0]!="@":
			line = line[:-1]
			parts = string.split(line,": ")
			fields = string.split(parts[0]," ")
			if fields[0]=="&":
				values = string.split(parts[1],", ")
				if (not words.has_key(fields[1])):
					words[fields[1]]=values
			elif fields[0]=="#":
				if (not words.has_key(fields[1])):
					words[fields[1]]=[]
		elif line=="\n":
			count = count + 1
		line = fp.readline()
	offsets = {}
	count = 0
	if len(words):
                keys = words.keys()
                keys.sort()
		print "<form action=\"http://www.w3.org/2002/01/update_dictionary\" method=\"post\"><ol>"
		for error in keys:
			print "<li>\"<span class='no'>%s</span>\" (<input type=\"checkbox\" name=\"list[]\" value=\"%s\"/> add to the dictionary)" % (error,error)

			if len(words[error]) and suggest:
				print "; suggestions:<ul class='suggestions'>"
				for option in words[error]:
					print "<li>%s</li>" % option
				print "</ul>"				
			print "</li>"
		print "</ol><p><label><input type=\"submit\" value=\"Update dictionary\"/> (W3C Comm Team only)</label></p></form>"
	else:
		print "<p><span class='yes'>No errors</span> found.</p>"

class URLLister(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []

    def start_a(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)

def traverse_site(parent_uri,lang,recursive):
	if ((parent_uri not in url_list) and re.search(base_domain,parent_uri)):
		url_list[parent_uri]=1
		print 'checking '+parent_uri
		SpellChecker(parent_uri,lang).start()    #call SpellChecker (separate thread and pass it the socket)

		if (recursive):
			sock = urllib.urlopen(parent_uri)
			parser = URLLister()
			parser.feed(sock.read())
			sock.close()
			parser.close()

			domain = urlparse.urlparse(parent_uri)[1] 
       
 			for uri in parser.urls:
				#if not a http url, turn it into one after parsing out the domain name from the base page
				if (re.match('mailto',uri) or re.match('javascript',uri)):
					continue
				if (not re.match('http',uri)):
					uri = 'http://'+domain+'/'+uri
				traverse_site(uri,lang,recursive) #do recursively if flag is set to 1

class SpellChecker(Thread):
  def __init__(self,uri,lang):
    Thread.__init__(self)
    self.uri = uri
    self.lang = lang

  def run(self):
    url_opener = urllib.FancyURLopener
    try:
	fp = urllib.urlopen(self.uri)
    except IOError, (errno, strerror):
	url_opener.error = "I/O error: %s %s" % (errno,strerror)
	fp = None	

    personal = "--personal=%s" % customized_dico
    if self.lang!="en":
        personal = ""
    command = "/usr/local/bin/lynx -nolist -dump -stdin|/usr/bin/aspell --lang %s -a %s --sug-mode=fast" % (self.lang,personal)

    (piperfd,pipewfd,pipeErr) = popen2.popen3(command)

    if (fp):
	pipewfd.write(fp.read())
	fp.close()
   	pipewfd.close()
        processingErrors=""
	if (processingErrors):
		print "<p>The following error occurred when trying to process your request :</p><pre class='no'>"
		print "</pre>"
                pipeErr.close()
	if (piperfd):
          	print "<h2>Errors found in the page</h2>"
          	format(piperfd,suggest)
                piperfd.close()
    else:
	print 'Could not check page spelling'

if __name__ == '__main__':
	if  os.environ.has_key('SCRIPT_NAME'):
		fields = cgi.FieldStorage()
		uri ="" 
		uri_text =""
		uri_text1=""
		suggest=0
		suggest_txt=''
		if fields.has_key('uri'):
			uri = fields['uri'].value
                elif fields.has_key('referrer') and os.environ.has_key('HTTP_REFERER'):
                        uri = os.environ['HTTP_REFERER']
                if uri:
			uri_text1="for %s" % (uri)
			uri_text=" for <a href=\"%s\">%s</a>" %(uri,uri)
                lang = "en"
                if fields.has_key('lang') and fields['lang'].value in languages.keys():
                        lang=fields['lang'].value
                languages_options = reduce(concat,map(format_option,languages.keys(),languages.values(),[lang for x in languages.keys()]))

		if fields.has_key('suggest'):
			if fields['suggest'].value=='on':
				suggest=1
				suggest_txt=" checked='checked'"
		if uri:
			if uri[:5] == 'file:' or len(urlparse.urlparse(uri)[0])<2:
				print "Status: 403"
				print "Content-Type: text/plain"
				print
				print "sorry, I decline to handle file: addresses"
			else:
				print Page1 % ('<meta name="ROBOTS" content="NOINDEX,NOFOLLOW"/>',uri_text1,uri_text,uri,languages_options,suggest_txt)
				base_domain = urlparse.urlparse(uri)[1] 

				if (fields.has_key('is_recursive') and fields['is_recursive']):
					traverse_site(uri,lang, 1)
				else:
					traverse_site(uri,lang, 0)
		else:
			print Page1 % ('',uri_text1,uri_text,uri,languages_options,suggest_txt)
		print Page2
