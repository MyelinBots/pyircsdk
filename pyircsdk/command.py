from abc import abstractmethod


class Command:
    def __init__(self):
        self.command = None
        self.args = [None]

    def parse(self, message):
        self.command = message[0]
        self.args = message[1:]
        return self


class Module:
    def __init__(self, irc, fantasy, command):
        self.irc = irc
        self.command = command
        self.fantasy = fantasy

    def startListening(self):
        self.irc.event.on('message', lambda x: print(x.command, x.messageFrom, x.messageTo, x.message))
        self.irc.event.on('message', lambda x: self.handleCommand(x, self.messageToCommandWithArgs(x)))
        self.irc.connect(None)

    def messageToCommandWithArgs(self, message):
        command = Command()
        if message is not None and message.message is not None:
            return command.parse(message.message.split(' '))
        return command

    @abstractmethod
    def handleCommand(self, message, command):
        pass
