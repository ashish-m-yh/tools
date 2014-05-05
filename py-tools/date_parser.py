import re

class DateParser():
	def __init__(self,date):
	    self._date = date

	def get_month(self):
		m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',self._date)

		if m is not None:
			_mon2num = dict({ 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 });

			month = list(m.groups())
			mon_num = _mon2num[month[0]]

			if mon_num < 10:
				return '0'+str(mon_num)
			else:
				return str(mon_num)

		return None

	def get_year(self):
		m = re.search(r'\D(\d{4})\D?', self._date)

		if m is not None:
			return str(list(m.groups())[0])

		return None

	def get_day(self):
		m = re.search(r'\D(\d{1,2})\D', self._date)

		if m is not None:
			day = list(m.groups())[0]
	
			if int(day) < 10:
				return '0'+str(day)
			else:
				return str(day)
			
		return None

	def get_time(self):
		m = re.search(r'(\d{1,2}):(\d{2})',self._date)

		if m is not None:
			time = list(m.groups())

			m1 = re.search(r'\D(AM|PM)\D?',self._date,re.IGNORECASE)

			if m1 is not None:
				tod = list(m1.groups())[0]
				if (tod.lower() == 'pm') and (time[0] < 12):
					time[0] = str(int(time[0]) + 12)
	
			return ":".join(time)				

	def get_date(self):
		y = self.get_year()
		m = self.get_month()
		d = self.get_day()
		t = self.get_time()

		dt = y+'-'+m+'-'+d
	
		if t is not None:
			dt = dt+' '+t

		return dt	
