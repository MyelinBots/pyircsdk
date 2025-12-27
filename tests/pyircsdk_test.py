import unittest
from unittest.mock import MagicMock, patch, call
import socket

from pyircsdk import IRCSDK, IRCSDKConfig


class TestIRCSDKMethods(unittest.TestCase):

    def test_create_irc(self):
        irc = IRCSDK(None)
        self.assertTrue(irc)
        self.assertIsNotNone(irc.event)
        self.assertEqual(irc._recv_buffer, '')

    def test_create_irc_with_config(self):
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            channel='#test',
            user='testuser',
            realname='Test Bot',
            ssl=False
        )
        irc = IRCSDK(config)
        self.assertEqual(irc.config, config)

    def test_create_irc_with_ssl_config(self):
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6697,
            nick='testbot',
            channel='#test',
            user='testuser',
            realname='Test Bot',
            ssl=True,
            allowAnySSL=False
        )
        irc = IRCSDK(config)
        self.assertTrue(irc.config.ssl)
        self.assertIsNotNone(irc.sslContext)

    def test_create_irc_with_ssl_allow_any(self):
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6697,
            ssl=True,
            allowAnySSL=True
        )
        irc = IRCSDK(config)
        self.assertFalse(irc.sslContext.check_hostname)

    def test_privmsg(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.privmsg('#channel', 'Hello, World!')
        irc.irc.send.assert_called_once_with(b'PRIVMSG #channel :Hello, World!\r\n')

    def test_privmsg_to_user(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.privmsg('someuser', 'Private message')
        irc.irc.send.assert_called_once_with(b'PRIVMSG someuser :Private message\r\n')

    def test_sendRaw(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.sendRaw('RAW COMMAND\r\n')
        irc.irc.send.assert_called_once_with(b'RAW COMMAND\r\n')

    def test_close(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, nick='testbot', ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.close()
        irc.irc.send.assert_called_once_with(b'QUIT :testbot\r\n')
        irc.irc.close.assert_called_once()

    def test_sendPassword(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.sendPassword('secretpass')
        irc.irc.send.assert_called_once_with(b'PASS secretpass\r\n')

    def test_join(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.join('#testchannel')
        irc.irc.send.assert_called_once_with(b'JOIN #testchannel\r\n')

    def test_setUser(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.setUser('testuser', 'Test Real Name')
        irc.irc.send.assert_called_once_with(b'USER testuser 0 * :Test Real Name\r\n')

    def test_setNick(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.setNick('testnick')
        irc.irc.send.assert_called_once_with(b'NICK testnick\r\n')

    def test_nickServIdentify(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.nickServIdentify('nickserv :identify %s', 'mypassword')
        irc.irc.send.assert_called_once_with(b'PRIVMSG nickserv :identify mypassword\r\n')

    def test_nickServIdentify_no_password(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        irc.nickServIdentify('nickserv :identify %s', None)
        irc.irc.send.assert_not_called()

    def test_connect_no_config_raises(self):
        irc = IRCSDK(None)
        irc.config = None
        with self.assertRaises(ValueError) as context:
            irc.connect()
        self.assertEqual(str(context.exception), 'No config passed to connect')

    @patch('pyircsdk.pyircsdk.socket.socket')
    def test_try_connect_success(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            channel='#test',
            user='testuser',
            realname='Test Bot',
            ssl=False,
            connectionTimeout=10
        )
        irc = IRCSDK(config)
        irc.startRecv = MagicMock()

        irc.try_connect(3, 1)

        mock_socket.connect.assert_called_once_with(('irc.example.com', 6667))
        mock_socket.settimeout.assert_any_call(10)

    @patch('pyircsdk.pyircsdk.socket.socket')
    @patch('pyircsdk.pyircsdk.time.sleep')
    def test_try_connect_retry_on_failure(self, mock_sleep, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = [
            socket.error("Connection refused"),
            socket.error("Connection refused"),
            None
        ]

        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            channel='#test',
            user='testuser',
            realname='Test Bot',
            ssl=False,
            connectionTimeout=10
        )
        irc = IRCSDK(config)
        irc.startRecv = MagicMock()

        irc.try_connect(3, 2)

        self.assertEqual(mock_socket.connect.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(2)

    @patch('pyircsdk.pyircsdk.socket.socket')
    @patch('pyircsdk.pyircsdk.exit')
    def test_try_connect_exhausted_retries_exits(self, mock_exit, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = socket.error("Connection refused")

        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            ssl=False,
            connectionTimeout=10
        )
        irc = IRCSDK(config)

        irc.try_connect(3, 0)

        mock_exit.assert_called_once_with(1)
        self.assertEqual(mock_socket.connect.call_count, 3)
        self.assertEqual(mock_socket.close.call_count, 3)


class TestIRCSDKParseMessage(unittest.TestCase):

    def setUp(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        self.irc = IRCSDK(config)

    def test_parse_message_privmsg(self):
        raw = ':nick!user@host PRIVMSG #channel :Hello world'
        data, prefix, command, params, trailing = self.irc.parse_message(raw)

        self.assertEqual(prefix, 'nick!user@host')
        self.assertEqual(command, 'PRIVMSG')
        self.assertIn('#channel', params)

    def test_parse_message_ping(self):
        raw = 'PING :server.example.com'
        data, prefix, command, params, trailing = self.irc.parse_message(raw)

        self.assertIsNone(prefix)
        self.assertEqual(command, 'PING')

    def test_parse_message_numeric_reply(self):
        raw = ':server.example.com 376 testnick :End of /MOTD command.'
        data, prefix, command, params, trailing = self.irc.parse_message(raw)

        self.assertEqual(prefix, 'server.example.com')
        self.assertEqual(command, '376')

    def test_parse_message_join(self):
        raw = ':nick!user@host JOIN #channel'
        data, prefix, command, params, trailing = self.irc.parse_message(raw)

        self.assertEqual(prefix, 'nick!user@host')
        self.assertEqual(command, 'JOIN')

    def test_parse_message_part(self):
        raw = ':nick!user@host PART #channel :Leaving'
        data, prefix, command, params, trailing = self.irc.parse_message(raw)

        self.assertEqual(prefix, 'nick!user@host')
        self.assertEqual(command, 'PART')


class TestIRCSDKHandleRawMessage(unittest.TestCase):

    def setUp(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        self.irc = IRCSDK(config)
        self.irc.irc = MagicMock()

    def test_handle_ping(self):
        raw = b'PING :server.example.com\r\n'
        self.irc.handle_raw_message(raw)
        self.irc.irc.send.assert_called_with(b'PONG server.example.com\r\n')

    def test_handle_motd_end_376(self):
        mock_callback = MagicMock()
        self.irc.event.on('connected', mock_callback)

        raw = b':server 376 nick :End of /MOTD command.\r\n'
        self.irc.handle_raw_message(raw)

        mock_callback.assert_called()

    def test_handle_motd_missing_422(self):
        mock_callback = MagicMock()
        self.irc.event.on('connected', mock_callback)

        raw = b':server 422 nick :MOTD File is missing\r\n'
        self.irc.handle_raw_message(raw)

        mock_callback.assert_called()

    def test_handle_multiple_messages(self):
        raw = b'PING :server1\r\nPING :server2\r\n'
        self.irc.handle_raw_message(raw)

        calls = self.irc.irc.send.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], call(b'PONG server1\r\n'))
        self.assertEqual(calls[1], call(b'PONG server2\r\n'))

    def test_handle_partial_message_buffering(self):
        """Test that partial messages are buffered correctly"""
        # First chunk - incomplete message
        self.irc.handle_raw_message(b'PING :serv')
        self.irc.irc.send.assert_not_called()

        # Second chunk - completes the message
        self.irc.handle_raw_message(b'er1\r\n')
        self.irc.irc.send.assert_called_once_with(b'PONG server1\r\n')

    def test_handle_partial_message_with_complete(self):
        """Test buffer with complete message followed by partial"""
        self.irc.handle_raw_message(b'PING :server1\r\nPING :ser')
        self.irc.irc.send.assert_called_once_with(b'PONG server1\r\n')

        self.irc.irc.send.reset_mock()
        self.irc.handle_raw_message(b'ver2\r\n')
        self.irc.irc.send.assert_called_once_with(b'PONG server2\r\n')

    def test_buffer_cleared_on_complete_messages(self):
        """Test that buffer is empty after processing complete messages"""
        self.irc.handle_raw_message(b'PING :server1\r\n')
        self.assertEqual(self.irc._recv_buffer, '')


class TestIRCSDKSetupListeners(unittest.TestCase):

    def test_setup_listeners_clears_old(self):
        """Test that _setup_listeners clears existing listeners"""
        config = IRCSDKConfig(
            host='irc.example.com',
            port=6667,
            nick='testbot',
            channel='#test',
            ssl=False
        )
        irc = IRCSDK(config)
        irc.irc = MagicMock()

        # Add some listeners
        mock1 = MagicMock()
        irc.event.on('raw', mock1)
        irc.event.on('connected', mock1)

        # Setup should clear them
        irc._setup_listeners()

        # Old listener should not be called
        irc.handle_raw_message(b'PING :test\r\n')
        mock1.assert_not_called()


if __name__ == '__main__':
    unittest.main()
