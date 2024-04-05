#!/usr/bin/env python3

import time, sys

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


sys.stdout.write('Importing modules (may take a while)... ')
sys.stdout.flush()
import authentik
from authentik_client.models.flow import Flow
import objects
import setup
import os
sys.stdout.write('\rImporting modules (may take a while)... done.\n')

nt = (True if os.name == 'nt' else False)
# print(f'System is {'nt' if nt else 'unix'}.')



def createInvite():
	knownGroups = authentik.fetchGroupList()
	knownInviteFlows: list[Flow] = authentik.fetchInviteFlows()

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

	newUser = objects.User(first, last, email, groupsToAdd, middleName=middleName, middleInitial=middleInitial, phone=phone, username=username)
	inviteObj = authentik.createInvite(newUser, knownInviteFlows[flowChoice].pk)




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
	while True:
		menu()