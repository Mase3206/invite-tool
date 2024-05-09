#!/usr/bin/env python3

import os
import time

import yaml
from authentik_client import Flow

import setup
from authentik import Authentik
from invite import InviteEmail
from mail import Email
from user import HomelabUser

global nt, headerText

nt = (True if os.name == 'nt' else False)
headerText = """

	 _____            _ _         _______          _ 
	|_   _|          (_) |       |__   __|        | |
	  | |  _ ____   ___| |_ ___     | | ___   ___ | |
	  | | | '_ \\ \\ / / | __/ _ \\    | |/ _ \\ / _ \\| |
	 _| |_| | | \\ V /| | ||  __/    | | (_) | (_) | |
	|_____|_| |_|\\_/ |_|\\__\\___|    |_|\\___/ \\___/|_|


"""


with open('conf.yml', 'r') as confFile:
	conf: dict = yaml.safe_load(confFile)


authObj = Authentik(conf['authentik'])



def header():
	"""
	Prints header text. Only used by CLI.
	"""

	print(headerText)
	print('Quickly create invites for Authentik and (if configured) Twingate.')
	print()



# CLI interactive invitation 
def createInvite() -> None:
	"""
	Interactive invitation helper tool. Used by CLI.
	"""
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

	groupsToAdd = input('Enter valid group name(s) separated by a space on the following line. Entering nothing will result in the user having broken permissions.\n : ').split(' ')


	newUser = HomelabUser(
		authObj,
		first, 
		last, 
		email, 
		groupsToAdd, 
		middleName=middleName, 
		middleInitial=middleInitial, 
		phone=phone, 
		username=username
	)

	print('\nConfirm the following information:')
	print(newUser.preview())
	proceed = input('Continue with user creation and invitation? [Y/n] ')
	if proceed.lower() == 'y' or proceed == '':
		pass
	else:
		print('Cancelling.')
		return

	print(f'Created HomelabUser object for {newUser.username}.')


	if not authObj.inviteExists(newUser):
		inviteObj = authObj.createInvite(newUser, knownInviteFlows[flowChoice])
		print(f'Created invitation in Authentik for {newUser.username}.')

		inviteEmail = InviteEmail(
			user=newUser,
			fromAddress=conf['fromAddr'],
			invite=inviteObj,
			flow=knownInviteFlows[flowChoice],
			authURL=conf['authentik']['url']
		)
		print(f'Created invite email for {newUser.username}. Will be sent from {conf['fromAddr']} to {newUser.email}.')

		inviteEmail.send(mailtrapApiKey=conf['mailtrap']['key'])
		print(f'Sent invite email to {newUser.email}.')

		print(f'Invitation success! Invite expires on {str(inviteObj.expires)}.')
		print(f'Invite token: {inviteObj.pk}')
		time.sleep(5)
		return

	else:
		print(f'ERROR: Invite for {newUser.username} already exists.')
		return



# CLI stuff
firstMenu = True
def menu() -> None:
	"""
	Interactive CLI menu.
	"""
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
	

def _test():
	m = Email('mr.skelly1285@gmail.com')
	print(m.addr)  # merp


if __name__ == '__main__':
	# _test()
	header()
	while True:
		menu()