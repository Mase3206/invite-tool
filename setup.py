#!/usr/bin/env python3

import yaml, json


__author__ = 'Noah S. Roberts'

"""
Configure invite-tool with Authentik and Twingate URLs and API keys. Meant to be ran directly, but can be imported as a module.
"""

confDefault = {
	'authentik': {
		'url': '',
		'key': ''
	},

	'twingate': {
		'use': '',
		'network': '',
		'key': ''
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



def headless(data: dict):
	return



def interactive():
	print(' --- Invite Tool Setup --- ')
	return


def cli():
	import argparse

	parser = argparse.ArgumentParser(description='Setup program for Invite Tool to configure Authentik and Twingate connections.')

	parser.add_argument('-v', action='store_true', help='Verbose output')
	parser.add_argument('--headless', type=json.loads, help='Headless mode; requires JSON data enclosed in a pair of single quotes.')

	args = parser.parse_args()
	print(args)

	if args.headless != None:
		headless(args.headless)
	else:
		interactive()

		




if __name__ == '__main__':
	cli()