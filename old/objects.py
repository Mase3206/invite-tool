import authentik
import twingate
import verify
import yaml
import smtplib




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



class InviteEmail:
	def __init__(
			self, 
			user: authentik.User, 
			fromAddress: str, 
			invite: authentik.Invitation, 
			flow: authentik.Flow,
			authURL: str
		):

		self.username = user.username
		self.name = user.fullName()
		self.toAddr = user.email
		self.fromAddr = fromAddress
		self.expires = invite.expires
		self.pk = invite.pk
		self.slug = flow.name
		self.inviteLink = f'https://{authURL}/if/flow/{self.slug}/?itoken={self.pk}'

		self.message = f"""\
		Subject: Welcome to das homelab!
		From: Authentik <{self.fromAddr}>
		To: {self.user.fullName()} <{self.toAddr}>
		
		Welcome to "das homelab", Noah's homelab running out of his dorm room! Below is the link to activate your new account... BUT, before you click it, please read the information below:

		- The username you are given cannot be easily changed.
		- The email this was sent to will be set as the primary email on your account. All homelab-related notifications, such as shared file alerts or password reset emails, will be sent here. This can be changed in the user settings inside Authentik.
		- At this point in time, you must be connected to Twingate to connect to das homelab.

		
		Also, take note of these important URLs:

		- Homepage (home.noahsroberts.com) - where links to all the things in the homelab live
		- Authentik (auth.noahsroberts.com) - the single sign-on system, prominently displaying the "das homelab" logo
		- Nextcloud (files.noahsroberts.com) - like Google Drive, but self-hosted and on steroids
		- BookStack (wiki.noahsroberts.com) - internal, user-facing wiki


		So, what is this email? Well, it's an invite. You are by no means obligated to accept it, but it would make your friend pretty dang happy. You might find some cool stuff in there, too. And, if you decide to pass for now but change your mind later, just let Noah know and he'll send you another invite.

		
		When you click the link below, it will automatically create a new user with the following information:
		- Name: {self.name}
		- Username: {self.username}
		- Email: {self.toAddr}
		

		Clicking the invite link will walk you through a brief enrollment process before presenting you with your Authentik dashboard.


		Invite link: {self.inviteLink}
		"""

	
	def mailtrapSend(self, apiKey):
		with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
			server.starttls()
			server.login("api", apiKey)
			server.sendmail(self.fromAddr, self.toAddr, self.message)





def _test():
	# testuser = User('Test', 'User', 'testuser@example.com', ['testing'], phone='10000000000')
	# print(testuser.createAuthInviteData())
	# authentik.createInvite(testuser)

	flows = authentik.fetchInviteFlows()
	print(flows)



if __name__ == '__main__':
	_test()