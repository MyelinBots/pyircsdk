import socket
import sys

from .event.event import Event
from .message import Message


class IRCSDK:
    def __init__(self, config):
        self.event = Event()
        if config:
            self.config = config
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def privmsg(self, receiver, msg):
        command = "PRIVMSG %s :%s\r\n" % (receiver, msg)
        self.irc.send(command.encode('utf-8'))

    def sendRaw(self, msg):
        self.irc.send(msg.encode('utf-8'))

    def close(self):
        message = "QUIT :%s\r\n" % self.config.nick
        self.irc.send(message.encode('utf-8'))
        self.irc.close()

    def connect(self, config):
        # if no config use __init__ config
        if not config:
            config = self.config

        # if no config is passed throw an error
        if not self.config:
            raise ValueError('No config passed to connect')

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print config
        print(config)

        self.irc.connect((self.config.host, self.config.port))
        self.event.emit('connected', 'Connected to host %s:%s' % (self.config.host, self.config.port))

        self.event.on('raw', self.log)
        self.event.on('raw', self.handle_raw_message)
        self.setUser(self.config.user)
        self.setNick(self.config.nick)
        self.event.on('connected', lambda data: self.join(self.config.channel))
        self.startRecv()

    def startRecv(self):
        while 1:
            try:
                text = self.irc.recv(2048)
                self.event.emit('raw', text)

            except OSError as e:
                print(e)
                # exit program
                sys.exit(1)
                break

    def log(self, data):
        # convert bytes to string
        data = data.decode('utf-8')
        # print(data)

    def join(self, channel):
        buffer = "JOIN %s\r\n" % channel
        self.irc.send(buffer.encode('utf-8'))

    def setUser(self, user):
        command = "USER %s 0 * :%s\r\n" % (user, user)
        self.irc.send(command.encode('utf-8'))

    def setNick(self, nick):
        command = "NICK %s\r\n" % nick
        self.irc.send(command.encode('utf-8'))

    def handle_raw_message(self, data):
        # parse message
        data = data.decode('utf-8')
        for line in data.split('\r\n'):
            if line:
                message, message_list, prefix, command, params, trailing = self.parse_message(line.encode('utf-8'))
                # print('Message: %s' % message)
                # print('Message List: %s' % message_list)
                # print('Prefix: %s' % prefix)
                # print('Command: %s' % command)
                # print('Params: %s' % params)
                # print('Trailing: %s' % trailing)

                # print('---')

                # handle ping
                if command == 'PING':
                    self.sendRaw('PONG ' + trailing + '\r\n')
                # find End of /MOTD command
                if command == '376':
                    self.event.emit('connected', 'End of /MOTD command.')

                # # find To connect type /QUOTE PONG
                # if data.find('To connect type /QUOTE PONG') != -1:
                #     print(data.split(':')[1])
                #     self.sendRaw('QUOTE PONG ' + data.split(':')[1] + '\r\n')

    def parse_message(self, data):
        # convert bytes to string
        data = data.decode('utf-8')

        # <message>  ::= [':' <prefix> <SPACE> ] <command> <params> <crlf>
        # <prefix>   ::= <servername> | <nick> [ '!' <user> ] [ '@' <host> ]
        # <command>  ::= <letter> { <letter> } | <number> <number> <number>
        # <SPACE>    ::= ' ' { ' ' }
        # <params>   ::= <SPACE> [ ':' <trailing> | <middle> <params> ]
        #
        # <middle>   ::= <Any *non-empty* sequence of octets not including SPACE
        #                or NUL or CR or LF, the first of which may not be ':'>
        # <trailing> ::= <Any, possibly *empty*, sequence of octets not including
        #                  NUL or CR or LF>
        #
        # <crlf>     ::= CR LF
        message = data.split()
        prefix = ''
        command = ''
        params = []
        trailing = ''
        if data.startswith(':') and len(message) > 1:
            prefix = message[0][1:]
            command = message[1]
            params = message[2:]
        else:
            prefix = None
            command = message[0]
            params = message[1:]

        if params:
            if params[0].startswith(':'):
                trailing = params[0][1:]
                params = params[1:]
            else:
                trailing = None
        messageFrom = prefix.split('!')[0] if prefix else None
        messageTo = params[0] if params else None
        # remove the first element from params
        actualMessage = ' '.join(params[1:]) if params else None
        # remove the ":" from the actual message
        if actualMessage:
            actualMessage = actualMessage[1:]

        self.event.emit('message',
                        Message(data, prefix, command, params, trailing, messageFrom, messageTo, actualMessage))

        return data, message, prefix, command, params, trailing

class IRCSDKConfig:
    def __init__(self, host, port, nick, channel, user):
        self.host = host
        self.port = port
        self.nick = nick
        self.channel = channel
        self.user = user

    def __str__(self):
        return f'Host: {self.host}, Port: {self.port}, Nick: {self.nick}, Channel: {self.channel}, User: {self.user}'

    def __repr__(self):
        return f'Host: {self.host}, Port: {self.port}, Nick: {self.nick}, Channel: {self.channel}, User: {self.user}'
