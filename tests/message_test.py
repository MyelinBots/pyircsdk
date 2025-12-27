import unittest
from pyircsdk import Message


class TestMessageMethods(unittest.TestCase):

    def test_create_message(self):
        msg = Message(
            data=':nick!user@host PRIVMSG #channel :Hello',
            prefix='nick!user@host',
            command='PRIVMSG',
            params=['#channel', ':Hello'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='Hello'
        )
        self.assertIsNotNone(msg)

    def test_message_attributes(self):
        msg = Message(
            data=':nick!user@host PRIVMSG #channel :Hello world',
            prefix='nick!user@host',
            command='PRIVMSG',
            params=['#channel', ':Hello', 'world'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='Hello world'
        )
        self.assertEqual(msg.data, ':nick!user@host PRIVMSG #channel :Hello world')
        self.assertEqual(msg.prefix, 'nick!user@host')
        self.assertEqual(msg.command, 'PRIVMSG')
        self.assertEqual(msg.params, ['#channel', ':Hello', 'world'])
        self.assertIsNone(msg.trailing)
        self.assertEqual(msg.messageFrom, 'nick')
        self.assertEqual(msg.messageTo, '#channel')
        self.assertEqual(msg.message, 'Hello world')

    def test_message_str(self):
        msg = Message(
            data=':nick!user@host PRIVMSG #channel :Hello',
            prefix='nick!user@host',
            command='PRIVMSG',
            params=['#channel'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='Hello'
        )
        result = str(msg)
        self.assertIn('nick!user@host', result)
        self.assertIn('PRIVMSG', result)
        self.assertIn('#channel', result)

    def test_message_with_none_values(self):
        msg = Message(
            data='PING :server',
            prefix=None,
            command='PING',
            params=[':server'],
            trailing=':server',
            messageFrom=None,
            messageTo=None,
            message=None
        )
        self.assertIsNone(msg.prefix)
        self.assertIsNone(msg.messageFrom)
        self.assertIsNone(msg.messageTo)
        self.assertIsNone(msg.message)

    def test_message_private_message(self):
        msg = Message(
            data=':sender!user@host PRIVMSG mynick :Private message',
            prefix='sender!user@host',
            command='PRIVMSG',
            params=['mynick', ':Private', 'message'],
            trailing=None,
            messageFrom='sender',
            messageTo='mynick',
            message='Private message'
        )
        self.assertEqual(msg.messageFrom, 'sender')
        self.assertEqual(msg.messageTo, 'mynick')
        self.assertEqual(msg.message, 'Private message')

    def test_message_join(self):
        msg = Message(
            data=':nick!user@host JOIN #channel',
            prefix='nick!user@host',
            command='JOIN',
            params=['#channel'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message=None
        )
        self.assertEqual(msg.command, 'JOIN')
        self.assertEqual(msg.messageFrom, 'nick')

    def test_message_part(self):
        msg = Message(
            data=':nick!user@host PART #channel :Goodbye',
            prefix='nick!user@host',
            command='PART',
            params=['#channel', ':Goodbye'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='Goodbye'
        )
        self.assertEqual(msg.command, 'PART')
        self.assertEqual(msg.message, 'Goodbye')

    def test_message_numeric_reply(self):
        msg = Message(
            data=':server 376 nick :End of /MOTD command.',
            prefix='server',
            command='376',
            params=['nick', ':End', 'of', '/MOTD', 'command.'],
            trailing=None,
            messageFrom='server',
            messageTo='nick',
            message='End of /MOTD command.'
        )
        self.assertEqual(msg.command, '376')
        self.assertEqual(msg.messageFrom, 'server')


if __name__ == '__main__':
    unittest.main()
