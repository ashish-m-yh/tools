import stream_parser
import re

class ResumeParser(stream_parser.StreamParser):
	def __init__(self,txt):
		self.set_text(txt)
		is_resume = self._is_resume()
		if not is_resume:
			raise Exception("Not a resume")

   	def _is_resume(self):
		c = 0
   		if (self._input is not None and len(self._input) > 0):
			m = []
        	m.append(re.findall("\s*Name\s+", self._input))
        	if len(m) > 0:
           		c = c + 1
			
			m = []
        	m.append(re.findall("\s*Education\s*", self._input))
        	m.append(re.findall("\s*Educational\s+qualification[s?]\s+", self._input, re.IGNORECASE))
        	m.append(re.findall("\s*Qualification[s?]\s+", self._input))
        	if len(m) > 0:
				c = c + 1

        	m = []
        	m.append(re.findall("\s*Contact\s+", self._input))
        	m.append(re.findall("\s*Personal\s+", self._input))
        	if len(m) > 0:
           		c = c + 1

	        m = []
        	m.append(re.findall("\s*skill|skills\s+", self._input, re.IGNORECASE))
	        if len(m) > 0:
				c = c + 1

	        m = []
        	m.append(re.findall("\s+Experience\s+", self._input))
        	m.append(re.findall("\s*Work experience\s+", self._input))
        	m.append(re.findall("\s*Work Experience\s+", self._input))
        	if len(m) > 0:
				c = c + 1
		
		return c >= 3
