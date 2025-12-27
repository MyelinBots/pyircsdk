import unittest
from pyircsdk import IRCSDKConfig


class TestIRCSDKConfigMethods(unittest.TestCase):

    def test_create_config_empty(self):
        config = IRCSDKConfig()
        self.assertIsNone(config.host)
        self.assertIsNone(config.port)
        self.assertIsNone(config.nick)
        self.assertIsNone(config.channel)
        self.assertIsNone(config.channels)
        self.assertIsNone(config.user)
        self.assertIsNone(config.realname)
        self.assertIsNone(config.password)
        self.assertIsNone(config.ssl)
        self.assertIsNone(config.nickservPassword)
        self.assertIsNone(config.nodataTimeout)
        self.assertIsNone(config.connectionTimeout)
        self.assertIsNone(config.allowAnySSL)
        # nickservFormat has a default
        self.assertEqual(config.nickservFormat, "nickserv :identify %s")

    def test_create_config_with_kwargs(self):
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            channel='#test',
            user='testuser',
            realname='Test Bot'
        )
        self.assertEqual(config.host, 'irc.example.com')
        self.assertEqual(config.port, 6667)
        self.assertEqual(config.nick, 'testbot')
        self.assertEqual(config.channel, '#test')
        self.assertEqual(config.user, 'testuser')
        self.assertEqual(config.realname, 'Test Bot')

    def test_create_config_with_ssl(self):
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6697,
            ssl=True,
            allowAnySSL=False
        )
        self.assertTrue(config.ssl)
        self.assertFalse(config.allowAnySSL)

    def test_create_config_with_channels_list(self):
        config = IRCSDKConfig(
            channels=['#channel1', '#channel2', '#channel3']
        )
        self.assertEqual(config.channels, ['#channel1', '#channel2', '#channel3'])

    def test_create_config_with_nickserv(self):
        config = IRCSDKConfig(
            nickservFormat='NS IDENTIFY %s',
            nickservPassword='secret123'
        )
        self.assertEqual(config.nickservFormat, 'NS IDENTIFY %s')
        self.assertEqual(config.nickservPassword, 'secret123')

    def test_create_config_with_timeouts(self):
        config = IRCSDKConfig(
            nodataTimeout=60,
            connectionTimeout=30
        )
        self.assertEqual(config.nodataTimeout, 60)
        self.assertEqual(config.connectionTimeout, 30)

    def test_config_str(self):
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            channel='#test',
            user='testuser'
        )
        result = str(config)
        self.assertIn('irc.example.com', result)
        self.assertIn('6667', result)
        self.assertIn('testbot', result)
        self.assertIn('#test', result)
        self.assertIn('testuser', result)

    def test_config_repr(self):
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            channel='#test',
            user='testuser'
        )
        result = repr(config)
        self.assertIn('irc.example.com', result)
        self.assertIn('6667', result)

    def test_default_nickserv_format(self):
        config = IRCSDKConfig()
        self.assertEqual(config.nickservFormat, "nickserv :identify %s")

    def test_custom_nickserv_format_overrides_default(self):
        config = IRCSDKConfig(nickservFormat='PRIVMSG NickServ :IDENTIFY %s')
        self.assertEqual(config.nickservFormat, 'PRIVMSG NickServ :IDENTIFY %s')


if __name__ == '__main__':
    unittest.main()
