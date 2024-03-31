import sys

from pyircsdk import IRCSDKConfig, IRCSDK, Module


class HelloModule(Module):
    def __init__(self, irc):
        super().__init__(irc, "", "hello")

    def handleCommand(self, message, command):
        if message.command == 'PRIVMSG':
            if command.command == self.fantasy+self.command and command.args[0] == 'pyirc':
                irc.privmsg(message.messageTo, "Hello, %s" % message.messageFrom)


class QuitModule(Module):
    def __init__(self, irc):
        super().__init__(irc, "!", "quit")

    def handleCommand(self, message, command):
        if message.command == 'PRIVMSG':
            if command.command == self.fantasy+self.command:
                irc.close()
                sys.exit(0)

irc = IRCSDK(IRCSDKConfig('irc.rizon.net',
                          6667,
                          'pyircsdk',
                          '#toolbot',
                          'pyircsdk'
                          ))

# irc.event.on('message', lambda x: handleCommand(irc, x.command, x.messageFrom, x.messageTo, x.message))
helloModule = HelloModule(irc)
quitModule = QuitModule(irc)
quitModule.startListening()
helloModule.startListening()

irc.connect(None)
