import sys
from pyircsdk import IRCSDKConfig, IRCSDK


def handleCommand(command, messageFrom, messageTo, message):
    if command == 'PRIVMSG':
        if message == 'hello pyirc':
            irc.privmsg(messageTo, "Hello, %s" % messageFrom)
        if message == 'quit':
            irc.close()
            sys.exit(0)


irc = IRCSDK(IRCSDKConfig('irc.rizon.net',
                          6667,
                          'pyircsdk',
                          '#toolbot',
                          'pyircsdk'
                          ))

irc.event.on('message', lambda x: print(x.command, x.messageFrom, x.messageTo, x.message))
irc.event.on('message', lambda x: handleCommand(x.command, x.messageFrom, x.messageTo, x.message))
irc.connect(None)
