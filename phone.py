import yaml


class PhoneFormat:
	"""
	Turns dict-type format spec into a Python class for easier type annotations
	"""
	def __init__(self, formatDict: dict[str, str|list[int | str]]):
		self.countryCode: str = formatDict['code']
		self.usedBy: list[str] = formatDict['countries']
		self.length: int = formatDict['length']
		self.grouping: list[int] = formatDict['grouping']
		self.divider: str = formatDict['divider']



class Phone:
	"""
	Phone object containing an unformatted phone number, the phone number region's format, and its "pretty" (formatted) representation
	"""
	def __init__(self, phoneNumber: str):
		with open('phone.yml', 'r') as f1:
			# explicit typing for type hints, because pyyaml can't do that automatically
			self.phone_formats: list[dict[str, str|list[int | str]]] = yaml.safe_load(f1)
		
		self.unformatted = phoneNumber
		self.regionFormat = self._findRegionFormat()
		self.pretty = self._formatPretty()

	
	def __str__(self) -> str:
		return self.pretty

	
	def _findRegionFormat(self) -> PhoneFormat:
		matched = {}

		for f in self.phone_formats:
			if f['code'] == self.unformatted[:len(f['code'])]:
				matched = f

		return PhoneFormat(matched)
		
	
	def _formatPretty(self) -> str:
		noCountryCode = self.unformatted[len(self.regionFormat.countryCode):]
		noDashes = []
		formatted = []

		for char in noCountryCode:
			if char == '-' or char == ' ':
				continue
			else:
				noDashes.append(char)
			
		noDashes = ''.join(noDashes)


		if len(noDashes) != self.regionFormat.length:
			print(f'Incorrect length for found country {self.regionFormat.countryCode}')
			return False
		

		group = 0
		lenWithGroups = self.regionFormat.grouping[0]

		for i in range(self.regionFormat.length):
			if i == lenWithGroups:
				formatted.append(self.regionFormat.divider)
				group += 1
				lenWithGroups += self.regionFormat.grouping[group]

			formatted.append(noDashes[i])
		
		return self.regionFormat.countryCode + ' ' + ''.join(formatted)
