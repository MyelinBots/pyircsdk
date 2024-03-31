import sys

from pyircsdk import Module


class HelloModule(Module):
    def __init__(self, irc):
        super().__init__(irc, "", "hello")

    def handleCommand(self, message, command):
        if message.command == 'PRIVMSG':
            if command.command == self.fantasy + self.command and command.args[0] == 'pyirc':
                self.irc.privmsg(message.messageTo, "Hello, %s" % message.messageFrom)
