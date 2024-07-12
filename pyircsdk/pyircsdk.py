import select
import socket
import ssl
import time
from dataclasses import dataclass

from .event.event import Event
from .message import Message

@dataclass
class IRCSDKConfig:
    host: str
    port: int
    nick: str
    channel: str
    channels: list[str]
    user: str
    realname: str
    password: str
    ssl: bool
    nickservFormat: str
    nickservPassword: str
    nodataTimeout: int
    connectionTimeout: int
    allowAnySSL: bool

    def __init__(self,  **kwargs):
        for k in self.__dataclass_fields__:
            setattr(self, k, None)

        for k, v in kwargs.items():
            setattr(self, k, v)
        if self.nickservFormat == None:
            self.nickservFormat = "nickserv :identify %s"

    def __str__(self):
        return f'Host: {self.host}, Port: {self.port}, Nick: {self.nick}, Channel: {self.channel}, User: {self.user}'

    def __repr__(self):
        return f'Host: {self.host}, Port: {self.port}, Nick: {self.nick}, Channel: {self.channel}, User: {self.user}'


class IRCSDK:
    def __init__(self, config: IRCSDKConfig = None) -> None:
        self.event: Event = Event()
        if config:
            self.config = config
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.config.ssl:
                self.sslContext = ssl.create_default_context()
                if self.config.allowAnySSL:
                    self.sslContext.check_hostname = False
                    self.sslContext.verify_mode = ssl.CERT_NONE

    def privmsg(self, receiver: str, msg: str) -> None:
        command = "PRIVMSG %s :%s\r\n" % (receiver, msg)
        self.irc.send(command.encode('utf-8'))

    def sendRaw(self, msg: str) -> None:
        self.irc.send(msg.encode('utf-8'))

    def close(self) -> None:
        message = "QUIT :%s\r\n" % self.config.nick
        self.irc.send(message.encode('utf-8'))
        self.irc.close()

    def sendPassword(self, password: str) -> None:
        message = f"PASS {password}\r\n"
        self.irc.send(message.encode('utf-8'))

    def connect(self, config: IRCSDKConfig = None) -> None:
        # if no config use __init__ config
        if not config:
            config = self.config

        # if no config is passed throw an error
        if not self.config:
            raise ValueError('No config passed to connect')
        self.irc: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.config.ssl:
            self.irc: socket.socket = self.sslContext.wrap_socket(self.irc, server_hostname=self.config.host)
        # print config
        print(config)

        # self.irc.connect((self.config.host, self.config.port))
        self.try_connect(5, 5)

    def try_connect(self, retries, wait_secs):
        for attempt in range(retries):
            self.irc.settimeout(self.config.connectionTimeout or 10)  # Set a timeout for the connection attempt

            try:
                print(f"Attempt {attempt + 1} of {retries}")
                self.irc.connect((self.config.host, self.config.port))
                print("Connection successful!")
                self.irc.settimeout(None)  # Reset the timeout to None (no timeout

                print('Connected to host %s:%s' % (self.config.host, self.config.port))
                self.event.emit('connected', 'Connected to host %s:%s' % (self.config.host, self.config.port))

                self.event.on('raw', self.log)
                self.event.on('raw', self.handle_raw_message)
                if self.config.password:
                    self.sendPassword(self.config.password)

                self.setUser(self.config.user, self.config.realname)
                self.setNick(self.config.nick)

                self.event.on('connected', lambda data: self.nickServIdentify(self.config.nickservFormat, self.config.nickservPassword))
                if self.config.channels:
                    self.event.on('connected', lambda data: [self.join(channel) for channel in self.config.channels])
                else:
                    self.event.on('connected', lambda data: self.join(self.config.channel))

                self.startRecv()
                break
            except socket.error as e:
                print(f"Connection failed: {e}")
                self.irc.close()  # Make sure to close the socket on failure
                if attempt < retries - 1:
                    print(f"Waiting for {wait_secs} seconds before retrying...")
                    time.sleep(wait_secs)
                else:
                    print("Maximum retry attempts reached, connection failed.")
                    raise

    def startRecv(self) -> None:
        while 1:
            # nodataTimeout or 120 seconds
            ready = select.select([self.irc], [], [], self.config.nodataTimeout or 120)
            if ready[0]:
                try:
                    data = self.irc.recv(2048)
                    if not data:
                        print("Connection closed by the remote host.")
                        break
                    self.event.emit('raw', data)

                except OSError as e:
                    print(e)
                    # exit program
                    break;
            else:
                if self.config.nodataTimeout > 0:
                    print("No data received for %s seconds, quiting..." % str(self.config.nodataTimeout or 120))
                    break

        # force program to close socket and to exit
        self.irc.close()
        exit(1)





    def log(self, data: bytes) -> None:
        # convert bytes to string
        data = data.decode('utf-8')
        # print(data)

    def join(self, channel: str) -> None:
        buffer = "JOIN %s\r\n" % channel
        self.irc.send(buffer.encode('utf-8'))

    def setUser(self, user: str, realname: str) -> None:
        command = "USER %s 0 * :%s\r\n" % (user, realname)
        self.irc.send(command.encode('utf-8'))

    def setNick(self, nick: str) -> None:
        command = "NICK %s\r\n" % nick
        self.irc.send(command.encode('utf-8'))

    def nickServIdentify(self, format: str, password: str) -> None:
        formated = format % password
        command = "PRIVMSG %s\r\n" % formated
        self.irc.send(command.encode('utf-8'))


    def handle_raw_message(self, data: bytes) -> None:
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
                    print('PING', trailing)
                    self.sendRaw('PONG ' + trailing + '\r\n')
                # find End of /MOTD command
                if command == '376' or command == '422':
                    self.event.emit('connected', 'End of /MOTD command.')

                # # find To connect type /QUOTE PONG
                # if data.find('To connect type /QUOTE PONG') != -1:
                #     print(data.split(':')[1])
                #     self.sendRaw('QUOTE PONG ' + data.split(':')[1] + '\r\n')

    def parse_message(self, data: bytes) -> tuple:
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
        messageFrom: str = prefix.split('!')[0] if prefix else None
        messageTo: str = params[0] if params else None
        # remove the first element from params
        actualMessage: str = ' '.join(params[1:]) if params else None
        # remove the ":" from the actual message
        if actualMessage:
            actualMessage: str = actualMessage[1:]

        self.event.emit('message',
                        Message(data, prefix, command, params, trailing, messageFrom, messageTo, actualMessage))

        return data, message, prefix, command, params, trailing

