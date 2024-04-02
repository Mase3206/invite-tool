#!/usr/bin/env python3

import yaml, json, time


__author__ = 'Noah S. Roberts'

"""
Configure invite-tool with Authentik and Twingate URLs and API keys. Meant to be ran directly, but can be imported as a module.
"""

confDefault = {
	'authentik': {
		'url': None,
		'key': None
	},

	'twingate': {
		'use': None,
		'network': None,
		'key': None
	}
}



def createConfFile():
	with open('conf.yml', 'w+') as f:
		yaml.safe_dump(
			confDefault,
			f
		)



def getExisting():
	with open('conf.yml', 'r') as f:
		try:
			existing = yaml.safe_load(f)
		
		# if file doesn't exist, offer to create it
		# once created, load its contents
		except FileNotFoundError:			
			proceed = input('conf.yml does not exist. Create it? [Y/n] ')

			if proceed.lower() == 'y' or proceed == '':
				createConfFile()
				existing = yaml.safe_load(f)
			else:
				print('Canceling.')
				exit(1)
		
		# return its contents
		finally:
			return existing
		


def writeConfFile(data: dict):
	with open('conf.yml', 'w') as f:
		yaml.safe_dump(data, f)



def headless(data: dict, ignore=False):
	# if an existing configuration exists and -i is not present, exit
	if getExisting() != confDefault and ignore != True:
		print('Configuration already present. Run script with `-i` to ignore.')
		exit(1)


	# create a copy of the default conf dict
	conf = confDefault.copy()
	unknownKeys = []

	for key in data.keys():
		if key in conf:
			conf[key] = data[key]
		
		# if key in data does not exist in confDefault copy, append it to the unknownKeys list
		else:
			unknownKeys.append(key)
	
	# return the unknown keys if it isn't empty;
	if len(unknownKeys) > 0:
		print('Found the following unknown keys:', end=' ')

		for key in unknownKeys:
			print(f'{key},', end=' ')
		
		print()

	writeConfFile(conf)
	print('Wrote conf successfully.')




def interactive(ignore=False):
	# if an existing configuration exists and -i is not present, exit
	if getExisting() != confDefault and ignore != True:
		print('It looks like Invite Tool has already been configured. If you would like to ignore and override this preexisting configuration, rerun this program again with the `-i` flag.')
		exit(1)


	print('\n --- Invite Tool Setup --- \n')
	if ignore == True:
		print('INFO: Ignore flag is present. Any preexisting configuration will be overwritten.')

	print('NOTE: When asked to input a URL, only input the domain name portion. Do not include the protocol or path.')
	conf = confDefault.copy()

	print('\nAuthentik configuration')
	conf['authentik']['url'] = input(' URL of server: ')
	conf['authentik']['key'] = input(' API key: ')

	print('\nTwingate configuration')
	conf['twingate']['use'] = input(' Configure Twingate [Y/n]: ')
	# only prompt for Twingate options if it is being configured
	if conf['twingate']['use'].lower() == 'y' or conf['twingate']['use'] == '':
		conf['twingate']['use'] = True  # store True for yaml
		conf['twingate']['network'] = input(' Network name (just the subdomain of twingate.com): ')
		conf['twingate']['key'] = input(' API key: ')
	else:
		conf['twingate']['use'] = False  # store False for yaml

	print('\n\nReview before saving')
	print('\n Authenitk')
	print(f'  URL: {conf['authentik']['url']}')
	print(f'  Key: {conf['authentik']['key']}')

	if conf['twingate']['use'] == True:
		print('\n Twingate (configured)')
		print(f'  Network name: {conf['twingate']['network']}')
		print(f'  Key: {conf['twingate']['key']}')

	else: 
		print('\n Twingate (not configured)')
	

	time.sleep(1)
	save = input('\nSave new config? [Y/n] ')
	if save.lower() == 'y' or save == '':
		writeConfFile(conf)
	else:
		print('Canceling.')
		exit(1)
	
	


def cli():
	import argparse

	parser = argparse.ArgumentParser(description='Setup program for Invite Tool to configure Authentik and Twingate connections.')

	parser.add_argument('-v', action='store_true', help='Verbose output')
	parser.add_argument('--headless', type=json.loads, help='Headless mode; requires JSON data enclosed in a pair of single quotes.')
	parser.add_argument('-i', action='store_true', default='store_false', help='Ignore and override any existing configuration.')

	args = parser.parse_args()
	# print(args)

	if args.headless != None:
		headless(args.headless)
	else:
		interactive()

		




if __name__ == '__main__':
	cli()