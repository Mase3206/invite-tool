import yaml


with open('verify/phone.yml', 'r') as f1:
	# explicit typing for type hints, because pyyaml can't do that automatically
	formats: list[dict[str, str|list[int | str]]] = yaml.safe_load(f1)



def findMatch(phoneNumber: str):
	matched = {}

	for f in formats:
		if f['code'] == phoneNumber[:len(f['code'])]:
			matched = f

	return matched
			


def formatPretty(phoneNumber: str, foundFormat: dict):
	noCountryCode = phoneNumber[len(foundFormat['code']):]
	noDashes = []
	formatted = []

	for char in noCountryCode:
		if char == '-' or char == ' ':
			continue
		else:
			noDashes.append(char)
		
	noDashes = ''.join(noDashes)


	if len(noDashes) != foundFormat['length']:
		print(f'Incorrect length for found country {foundFormat['code']}')
		return False
	

	group = 0
	lenWithGroups = foundFormat['grouping'][0]

	for i in range(foundFormat['length']):
		if i == lenWithGroups:
			formatted.append(foundFormat['divider'])
			group += 1
			lenWithGroups += foundFormat['grouping'][group]

		formatted.append(noDashes[i])
	
	return foundFormat['code'] + ' ' + ''.join(formatted)
	


def _test():
	n = '14062173981'
	f = findMatch(n)
	p = formatPretty(n, f)
	print(p)


if __name__ == '__main__':
	_test()