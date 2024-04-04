def check(email: str) -> bool:
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
