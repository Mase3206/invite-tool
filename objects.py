import authentik
import twingate
import verify
import yaml
from collections import OrderedDict



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
		middleName (str): user's middle name
		middleInitial (str): user's middle inital; not used if middleName is set
	"""

	def __init__(self, firstName: str, lastName: str, email: str, groups: list[str], middleName='', middleInitial='', phone='', username=''):
		self.first = firstName
		self.last = lastName

		self.middleName = middleName
		self.middleInitial = middleInitial


		knownUsers = authentik.fetchUserList()

		if username == '':
			self.username = self.makeUsername()
		else:
			self.username = username

		if self.username in knownUsers:
			raise ExistsError(f'User {self.username} already exists.')


		knownGroups = authentik.fetchGroupList()
		for group in groups:
			if group not in knownGroups:
				print(f'Unknown group {group}. Removing from list.')
				groups.remove(group)
		self.groups = groups



		if verify.email_check(email):
			self.email = email
		else:
			raise ValueError(f'{email} is not a valid email.')


		if phone != '':
			phoneRegion = verify.phone_findMatch(phone)
			self.phone = verify.phone_formatPretty(phone, phoneRegion)
		else:
			self.phone = ''


	
	def makeUsername(self) -> str:
		with open('conf.yml', 'r') as f:
			usernameFormat: list[dict[str, str | None]] = yaml.safe_load(f)['formats']['username']

		# separator
		if usernameFormat['separator'] != None:
			sep1 = usernameFormat['separator']
			sep2 = usernameFormat['separator']
		else:
			sep1 = ''
			sep2 = ''
		
		# first name
		if usernameFormat['first'] == 'full':
			first = self.first.lower()
		elif usernameFormat['first'] == 'initial':
			first = self.first.lower()[0]
		else:
			first = ''
			sep1 = ''

		# middle name
		if usernameFormat['middle'] == 'full':
			middle = self.middleName.lower()
		elif usernameFormat['middle'] == 'initial':
			middle = self.middleInitial.lower()
		else:
			middle = ''
			sep2 = ''

		# first name
		if usernameFormat['last'] == 'full':
			last = self.last.lower()
		elif usernameFormat['last'] == 'initial':
			last = self.last.lower()[0]
		else:
			last = ''

		return f'{first}{sep1}{middle}{sep2}{last}'




	def fullName(self) -> str:
		if self.middleInitial != '':
			if self.middleName != '':
				return f'{self.first} {self.middleName} {self.last}'
			else:
				return f'{self.first} {self.middleInitial}. {self.last}'
		else:
			return f'{self.first} {self.last}'



	def createAuthInviteData(self) -> dict:
		return {
			'name': self.fullName(),
			'username': self.username,
			'email': self.email,
			'phone': self.phone,
			'groups_to_add': self.groups,
			'invite_expires': ''
		}










def _test():
	# testuser = User('Test', 'User', 'testuser@example.com', ['testing'], phone='10000000000')
	# print(testuser.createAuthInviteData())
	# authentik.createInvite(testuser)

	flows = authentik.fetchInviteFlows()
	print(flows)



if __name__ == '__main__':
	_test()