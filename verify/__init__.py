"""
Some modules to help verify the correctness of information. Not 100% accurate.

Verifies: 
* phone numbers
* emails
"""


class MalformedError(ValueError):
	pass


class TheFuck(Exception):
	pass