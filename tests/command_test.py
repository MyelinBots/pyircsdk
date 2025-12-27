import unittest
from unittest.mock import MagicMock
from pyircsdk import Command, Module, Message, IRCSDK, IRCSDKConfig


class TestCommandMethods(unittest.TestCase):

    def test_create_command(self):
        cmd = Command()
        self.assertIsNone(cmd.command)
        self.assertEqual(cmd.args, [None])

    def test_parse_command(self):
        cmd = Command()
        result = cmd.parse(['!hello', 'arg1', 'arg2'])
        self.assertEqual(cmd.command, '!hello')
        self.assertEqual(cmd.args, ['arg1', 'arg2'])
        self.assertEqual(result, cmd)

    def test_parse_command_no_args(self):
        cmd = Command()
        cmd.parse(['!ping'])
        self.assertEqual(cmd.command, '!ping')
        self.assertEqual(cmd.args, [])

    def test_parse_command_single_arg(self):
        cmd = Command()
        cmd.parse(['!echo', 'message'])
        self.assertEqual(cmd.command, '!echo')
        self.assertEqual(cmd.args, ['message'])

    def test_parse_command_many_args(self):
        cmd = Command()
        cmd.parse(['!cmd', 'a', 'b', 'c', 'd', 'e'])
        self.assertEqual(cmd.command, '!cmd')
        self.assertEqual(cmd.args, ['a', 'b', 'c', 'd', 'e'])


class TestModuleMethods(unittest.TestCase):

    def setUp(self):
        config = IRCSDKConfig(host='irc.example.com', port=6667, ssl=False)
        self.irc = IRCSDK(config)

    def test_create_module(self):
        module = TestModule(self.irc, '!', 'test')
        self.assertEqual(module.irc, self.irc)
        self.assertEqual(module.fantasy, '!')
        self.assertEqual(module.command, 'test')

    def test_start_listening(self):
        module = TestModule(self.irc, '!', 'test')
        initial_listeners = len(self.irc.event.listeners.get('message', []))
        module.startListening()
        new_listeners = len(self.irc.event.listeners.get('message', []))
        self.assertEqual(new_listeners, initial_listeners + 1)

    def test_message_to_command_with_args(self):
        module = TestModule(self.irc, '!', 'test')
        msg = Message(
            data=':nick!user@host PRIVMSG #channel :!hello arg1 arg2',
            prefix='nick!user@host',
            command='PRIVMSG',
            params=['#channel'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='!hello arg1 arg2'
        )
        cmd = module.messageToCommandWithArgs(msg)
        self.assertEqual(cmd.command, '!hello')
        self.assertEqual(cmd.args, ['arg1', 'arg2'])

    def test_message_to_command_with_args_no_args(self):
        module = TestModule(self.irc, '!', 'test')
        msg = Message(
            data=':nick!user@host PRIVMSG #channel :!ping',
            prefix='nick!user@host',
            command='PRIVMSG',
            params=['#channel'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='!ping'
        )
        cmd = module.messageToCommandWithArgs(msg)
        self.assertEqual(cmd.command, '!ping')
        self.assertEqual(cmd.args, [])

    def test_message_to_command_with_none_message(self):
        module = TestModule(self.irc, '!', 'test')
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
        cmd = module.messageToCommandWithArgs(msg)
        self.assertIsNone(cmd)

    def test_message_to_command_with_none_input(self):
        module = TestModule(self.irc, '!', 'test')
        cmd = module.messageToCommandWithArgs(None)
        self.assertIsNone(cmd)

    def test_handle_message_calls_handle_command(self):
        module = TestModule(self.irc, '!', 'test')
        module.handleCommand = MagicMock()

        msg = Message(
            data=':nick!user@host PRIVMSG #channel :!test arg',
            prefix='nick!user@host',
            command='PRIVMSG',
            params=['#channel'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='!test arg'
        )
        module.handleMessage(msg)
        module.handleCommand.assert_called_once()

    def test_handle_message_calls_handle_error_on_exception(self):
        module = TestModule(self.irc, '!', 'test')
        module.handleCommand = MagicMock(side_effect=Exception("Test error"))
        module.handleError = MagicMock()

        msg = Message(
            data=':nick!user@host PRIVMSG #channel :!test',
            prefix='nick!user@host',
            command='PRIVMSG',
            params=['#channel'],
            trailing=None,
            messageFrom='nick',
            messageTo='#channel',
            message='!test'
        )
        module.handleMessage(msg)
        module.handleError.assert_called_once()


class TestModule(Module):
    """Concrete implementation of Module for testing"""

    def handleCommand(self, message, command):
        pass

    def handleError(self, message, command, error):
        pass


if __name__ == '__main__':
    unittest.main()
