import time
import unittest

from pyircsdk.pyircsdk import IRCSDK


class TestIRCSDKMethods(unittest.TestCase):

    def test_create_irc(self):
        irc = IRCSDK(None)
        self.assertTrue(irc)

    # def test_connect(self):
    #     irc = IRCSDK({
    #         'host': 'pyircsdk.rizon.net',
    #         'port': 6667,
    #         'nick': 'testtest-pyechat',
    #         'channel': '#pyechat',
    #     })
    #     irc.connect(None)
    #     # sleep for 10 seconds
    #     time.sleep(10)
    #     # pyircsdk.join('#pyechat')
    #     # self.assertTrue(pyircsdk.pyircsdk)
    #
    # def test_onconnect(self):
    #     irc = IRCSDK()
    #     irc.connect()
    #     self.assertTrue(irc.event)

