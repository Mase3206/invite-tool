"""
Some modules to help verify the correctness of information. Not 100% accurate.

Verifies: 
* phone numbers
* emails
"""

from verify import *
from verify import __doc__

class MalformedError(ValueError):
	pass


class TheFuck(Exception):
	pass


__all__ = ('email', 'phone')