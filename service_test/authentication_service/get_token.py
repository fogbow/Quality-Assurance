import requests

from ..common import TestSuite

__all__ = ['AuthTest']

class AuthTest(TestSuite):

	def __init__(self):
		super(TestSuite, self).__init__()
		
	@classmethod
	def run(self):
		self.logTest("jhkjhkh")

	def test_auth(self):
		print("hjkh")

if __name__ == "__main__" :
	AuthTest.run()
