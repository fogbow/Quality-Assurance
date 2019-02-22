import requests

from common import TestSuite

__all__ = ['AuthTest']

class AuthTest(TestSuite):

    test_number = 0

    def __init__(self):
        self.test_auth()

    def test_auth(self):
        super().logTest("Success get token")
        # self.getToken()

    # def getToken(self):
    #     payload = {
    #         'username': 
    #     }
    #     requests.get
    
    