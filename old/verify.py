
import yaml


with open('phone.yml', 'r') as f1:
	# explicit typing for type hints, because pyyaml can't do that automatically
	phone_formats: list[dict[str, str|list[int | str]]] = yaml.safe_load(f1)



def phone_findMatch(phoneNumber: str):
	matched = {}

	for f in phone_formats:
		if f['code'] == phoneNumber[:len(f['code'])]:
			matched = f

	return matched
			


def phone_formatPretty(phoneNumber: str, foundFormat: dict):
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



def email_check(email: str) -> bool:
	try:
		prefix = email.split('@')[0]
		domain = email.split('@')[1].split('.')[0]
		tld = email.split('.')[1]

		if domain == 'localhost':
			reconstruct = f'{prefix}@localhost'

			# check if any part is empty
			if '' in [prefix]:
				return False

			# reconstruct it and verify against original
			if reconstruct == email:
				return True
			else:
				return False
		
		else:
			reconstruct = f'{prefix}@{domain}.{tld}'

			# check if any part is empty
			if '' in [prefix, domain, tld]:
				return False

			# reconstruct it and verify against original
			if reconstruct == email:
				return True
			else:
				return False
		
	# if any part is missing, return False
	except IndexError:
		return False



def _test():
	n = '14062173981'
	f = phone_findMatch(n)
	p = phone_formatPretty(n, f)
	print(p)


if __name__ == '__main__':
	_test()