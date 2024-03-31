import sys

from pyircsdk import Module


class QuitModule(Module):
    def __init__(self, irc):
        super().__init__(irc, "!", "quit")

    def handleCommand(self, message, command):
        if message.command == 'PRIVMSG':
            if command.command == self.fantasy+self.command:
                self.irc.close()
                sys.exit(0)