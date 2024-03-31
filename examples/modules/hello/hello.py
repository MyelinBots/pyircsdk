
def handleCommand(irc, command, messageFrom, messageTo, message):
    if command == 'PRIVMSG':
        if message == 'hello pyirc':
            irc.privmsg(messageTo, "Hello, %s" % messageFrom)
        if message == 'quit':
            irc.close()
            sys.exit(0)