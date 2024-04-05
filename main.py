#!/usr/bin/env python3

import datetime
import os
import smtplib
import sys
import time

import authentik_client as ac
import yaml
from authentik_client.models.flow import Flow
from authentik_client.models.flow_designation_enum import FlowDesignationEnum
from authentik_client.models.invitation import Invitation
from authentik_client.models.invitation_request import InvitationRequest


import setup
import twingate



global nt, headerText


with open('conf.yml', 'r') as f1:
	conf: dict[dict[str, str] | str, str] = yaml.safe_load(f1)



class ExistsError(Exception):
	pass



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



class Email:
	"""
	Email object that checks for validity of given email when initalized.
	"""
	def __init__(self, email: str):
		self.prefix = email.split('@')[0]
		self.domain = email.split('@')[1].split('.')[0]
		self.tld = email.split('.')[1]

		if self.domain == 'localhost':
			self.addr = f'{self.prefix}@localhost'
		
		else:
			self.addr = f'{self.prefix}@{self.domain}.{self.tld}'
	
	
	def __str__(self) -> str:
		return self.addr
	
	
	def __repr__(self) -> str:
		return f'pre={self.prefix}, domain={self.domain}, tld={self.tld}'




class HomelabUser:
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


		knownUsers = authObj.fetchUserList()

		if username == '':
			self.username = self._makeUsername()
		else:
			self.username = username

		if self.username in knownUsers:
			raise ExistsError(f'User {self.username} already exists.')


		knownGroups = authObj.fetchGroupList()
		for group in groups:
			if group not in knownGroups:
				print(f'Unknown group {group}. Removing from list.')
				groups.remove(group)
		self.groups = groups



		self.email = Email(email).addr


		if phone != '':
			self.phone = Phone(phone).pretty
		else:
			self.phone = ''

	
	def _makeUsername(self) -> str:
		with open('conf.yml', 'r') as f:
			usernameFormat: list[dict[str, str | None]] = yaml.safe_load(f)['formats']['username']

		# separator
		if usernameFormat['separator'] != '':
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
			user: HomelabUser, 
			fromAddress: str, 
			invite: Invitation, 
			flow: Flow,
			authURL: str
		):

		self.username = user.username
		self.name = user.fullName()
		self.toAddr = user.email
		self.fromAddr = fromAddress
		self.expires = invite.expires
		self.pk = invite.pk
		self.slug = flow.slug
		self.inviteLink = f'https://{authURL}/if/flow/{self.slug}/?itoken={self.pk}'

		self.message = f"""\
Subject: Welcome to das homelab!
To: {self.name} <{self.toAddr}>
From: Authentik <{self.fromAddr}>

Welcome to "das homelab", Noah's homelab running out of his dorm room! Below is the link to activate your new account... BUT, before you click it, please read the information below:

* The username you are given cannot be easily changed.
* The email this was sent to will be set as the primary email on your account. All homelab-related notifications, such as shared file alerts or password reset emails, will be sent here. This can be changed in the user settings inside Authentik.
* At this point in time, you must be connected to Twingate to connect to das homelab.


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



class Authentik:
	def __init__(self, authConf: dict[str, str]):
		self.authConf = authConf
		# configure API client
		configuration = ac.Configuration(
			host = f'https://{authConf['url']}/api/v3', 
			api_key = {
				'authentik': authConf['key']
			}
		)

		# set api key
		configuration.api_key['authentik'] = authConf['key']


		APIClient = ac.ApiClient(configuration)

		# create API objects for each API classification
		# admin = ac.AdminApi(APIClient)
		# authenticators = ac.AuthenticatorsApi(APIClient)
		self.core = ac.CoreApi(APIClient)
		# crypto = ac.CryptoApi(APIClient)
		# enterprise = ac.EnterpriseApi(APIClient)
		# events = ac.EventsApi(APIClient)
		self.flows = ac.FlowsApi(APIClient)
		# managed = ac.ManagedApi(APIClient)
		# oauth2 = ac.Oauth2Api(APIClient)
		# outposts = ac.OutpostsApi(APIClient)
		# policies = ac.PoliciesApi(APIClient)
		# propertyMappings = ac.PropertymappingsApi(APIClient)
		# providers = ac.ProvidersApi(APIClient)
		# RAC = ac.RacApi(APIClient)
		# RBAC = ac.RbacApi(APIClient)
		# root = ac.RootApi(APIClient)
		# schema = ac.SchemaApi(APIClient)
		# sources = ac.SourcesApi(APIClient)
		self.stages = ac.StagesApi(APIClient)
		# tenants = ac.TenantsApi(APIClient)
	
	def fetchGroupList(self) -> list[str]:
		# grab results section of the raw ouput
		raw = self.core.core_groups_list().results

		# make a list of all the group names
		groups = [g.name for g in raw]
		# print(groups)
		return groups



	def fetchUserList(self) -> list[str]:
		# grab results section of the raw ouput
		raw = self.core.core_users_list().results

		# make a list of usernames from the authentik_client.User object
		users = [u.username for u in raw]
		# print(users)
		return users



	def fetchInviteFlows(self) -> list[Flow]:
		raw: list[Flow] = self.flows.flows_instances_list().results
		enrollmentFlows = []

		for flow in raw:
			if flow.designation == FlowDesignationEnum.ENROLLMENT:
				enrollmentFlows.append(flow)

		a: Flow = enrollmentFlows[0]

		return enrollmentFlows



	def shiftDate(self, ref: datetime, days: int) -> datetime:	
		return ref + datetime.timedelta(days=days)



	def createInvite(self, user: HomelabUser, flow: Flow):
		today = datetime.datetime.today()
		expires = self.shiftDate(today, +14)

		data = user.createAuthInviteData()
		data['invite_expires'] = str(expires)

		invite = InvitationRequest(
			name=f'{user.username}-invite',
			expires=expires,
			fixed_data=data,
			single_use=True,
			flow=flow.pk,
		)

		return self.stages.stages_invitation_invitations_create(invite)


authObj = Authentik(conf['authentik'])



def header():
	global nt, headerText
	headerText = """

	 _____            _ _         _______          _ 
	|_   _|          (_) |       |__   __|        | |
	  | |  _ ____   ___| |_ ___     | | ___   ___ | |
	  | | | '_ \\ \\ / / | __/ _ \\    | |/ _ \\ / _ \\| |
	 _| |_| | | \\ V /| | ||  __/    | | (_) | (_) | |
	|_____|_| |_|\\_/ |_|\\__\\___|    |_|\\___/ \\___/|_|


	"""
	print(headerText)
	print('Quickly create invites for Authentik and (if configured) Twingate.')
	print()

	nt = (True if os.name == 'nt' else False)



def createInvite():
	knownGroups = authObj.fetchGroupList()
	knownInviteFlows: list[Flow] = authObj.fetchInviteFlows()

	print('\n ** New invite ** \n')

	print(f'Choose an invite flow:')
	for i in range(len(knownInviteFlows)):
		print(f' {i + 1}. {knownInviteFlows[i].name}')
	flowChoice = int(input('  : ')) - 1


	# get all that juicy info
	first = input('\nFirst name: ')
	middleName = input('Middle name (leave empty for none): ')
	middleInitial = input('Middle initial (leave empty for none): ')
	last = input('Last name: ')
	username = input('Username (leave emtpy for auto): ')
	email = input('Email: ')
	phone = input('Phone number (leave empty for none): ')
	
	print('\nValid groups:', end=' ')
	for g in knownGroups:
		print(g, end=' ')
	print()

	groupsToAdd = input('Enter valid group name(s) separated by a space on the following line. Entering nothing will result in the user having broken permissions.\n : ')
	if groupsToAdd == '':
		groupsToAdd = []
	else:
		groupsToAdd = groupsToAdd.split(' ')

	newUser = HomelabUser(first, last, email, groupsToAdd, middleName=middleName, middleInitial=middleInitial, phone=phone, username=username)
	inviteObj = authObj.createInvite(newUser, knownInviteFlows[flowChoice])
	inviteEmail = InviteEmail(
		user=newUser,
		fromAddress=conf['fromAddr'],
		invite=inviteObj,
		flow=knownInviteFlows[flowChoice],
		authURL=conf['authentik']['url']
	)
	inviteEmail.mailtrapSend(conf['mailtrap']['key'])



# CLI stuff
firstMenu = True
def menu():
	global firstMenu

	# print(firstMenu)
	if firstMenu:
		print()
		firstMenu = False
	else:
		os.system('cls' if nt else 'clear')

	print('Options:')

	setupExists = setup.getExisting() != setup.confDefault
	options = [
		'Initial setup',
		'Create invite',
		'Exit'
	]

	for i in range(len(options)):
		print(f' {i + 1}. {options[i]}')

	choice = input('  : ')
	try:
		choice = int(choice)
	except ValueError:
		print(f'Please enter a number.')
		return
	
	if choice == 1:
		if setupExists:
			clearExisting = input('\nExisting setup present. Would you like to clear it? [y/N] ')

			if clearExisting.lower() == 'n' or clearExisting == '':
				print('Canceling.\nReturning to main menu.')
				time.sleep(1)
				return
			
			else:
				print('Clearing existing config.')
				setup.writeConfFile(setup.confDefault)
				print('Returning to main menu.')
				time.sleep(1)
				return

		else: 
			setup.interactive()
			print('\nReturning to main menu.')
			time.sleep(1)
			return

	elif choice == 2:
		createInvite()
		print('Returning to main menu.')
		time.sleep(1)
		return
	
	elif choice == 3:
		exit(0)
	
	else:
		print(f'Unknown option {choice}.\nReturning to main menu.')
		time.sleep(1)
		return
	


if __name__ == '__main__':
	header()
	while True:
		menu()