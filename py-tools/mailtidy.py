import re

def mailtidy(filename): 
	mailtext = ''

	with open(filename,"r") as f:
		data = f.readlines()
		l = len(data)

		check_line = False

		for i in xrange(0,l):
			if len(data)-1 < i:
				break

			line = data[i]

			if line.startswith('To:') or line.startswith('Cc'):
				check_line = True
			elif check_line:
				check_line = False
				if not(re.search(r'^$',line) or re.search(r':',line)):
					data[i-1] = data[i-1].rstrip()+data[i]
					data.pop(i)
					l = l - 1

		mailtext = "".join(data)
	f.closed

	return mailtext
