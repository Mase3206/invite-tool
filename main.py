from verify import email as e, phone as p
import authentik
import twingate




class ExistsError(Exception):
	pass



class User:
	"""
	User Object
	=====================

	Holds an Authentik user's first and last name, username, email, and optional attributes for use in a user invitation.

	Required attributes (args)
	--------------------------
		firstName (str): user's first name
		lastName (str): user's last name
		email (str): user's email

	Optional attributes (kwargs)
	----------------------------
		phone (str): user's phone number. Must include "+" country code and area code. Do not use dashes.
		username (str): force username
	"""

	def __init__(self, firstName: str, lastName: str, email: str, groups: list, phone='', username=''):
		knownUsers = authentik.fetchUserList()
		self.username = firstName.lower()[0] + lastName.lower() if username == '' else username.lower()
		print(f'this {self.username}')
		if self.username in knownUsers:
			raise ExistsError(f'User {self.username} already exists.')


		self.first = firstName
		self.last = lastName

		knownGroups = authentik.fetchGroupList()
		for group in groups:
			if group not in knownGroups:
				print(f'Unknown group {group}. Removing from list.')
				groups.remove(group)
		self.groups = groups

		if e.check(email):
			self.email = email
		
		if phone != '':
			phoneRegion = p.findMatch(phone)
			self.phone = p.formatPretty(phone, phoneRegion)



def _test():
	noah = User('Noah', 'Roberts', 'noah10838@gmail.com', ['user', 'admin'], phone='14062173981')



if __name__ == '__main__':
	_test()