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
        if self.nickservFormat is None:
            self.nickservFormat = "nickserv :identify %s"

    def __str__(self):
        return f'Host: {self.host}, Port: {self.port}, Nick: {self.nick}, Channel: {self.channel}, User: {self.user}'

    def __repr__(self):
        return f'Host: {self.host}, Port: {self.port}, Nick: {self.nick}, Channel: {self.channel}, User: {self.user}'


class IRCSDK:
    def __init__(self, config: IRCSDKConfig = None) -> None:
        self.event: Event = Event()
        self._recv_buffer = ''
        if config:
            self.config = config
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
        if not config:
            config = self.config

        if not self.config:
            raise ValueError('No config passed to connect')

        print(config)
        self.try_connect(5, 5)

    def _setup_listeners(self) -> None:
        """Set up event listeners (only called once per connection)"""
        self.event.remove_all('raw')
        self.event.remove_all('connected')

        self.event.on('raw', self.handle_raw_message)

        def on_connected(data):
            self.nickServIdentify(self.config.nickservFormat, self.config.nickservPassword)
            if self.config.channels:
                for channel in self.config.channels:
                    self.join(channel)
            elif self.config.channel:
                self.join(self.config.channel)

        self.event.on('connected', on_connected)

    def try_connect(self, retries, wait_secs):
        for attempt in range(retries):
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.config.ssl:
                self.irc = self.sslContext.wrap_socket(self.irc, server_hostname=self.config.host)
            self.irc.settimeout(self.config.connectionTimeout or 10)

            try:
                print(f"Attempt {attempt + 1} of {retries}")
                self.irc.connect((self.config.host, self.config.port))
                print("Connection successful!")
                self.irc.settimeout(None)

                print('Connected to host %s:%s' % (self.config.host, self.config.port))

                self._setup_listeners()
                self._recv_buffer = ''

                if self.config.password:
                    self.sendPassword(self.config.password)

                self.setUser(self.config.user, self.config.realname)
                self.setNick(self.config.nick)

                self.startRecv()
                return
            except socket.error as e:
                print(f"Connection failed: {e}")
                self.irc.close()
                if attempt < retries - 1:
                    print(f"Waiting for {wait_secs} seconds before retrying...")
                    time.sleep(wait_secs)

        print("Maximum retry attempts reached, connection failed.")
        exit(1)

    def startRecv(self) -> None:
        while True:
            ready = select.select([self.irc], [], [], self.config.nodataTimeout or 120)
            if ready[0]:
                try:
                    data = self.irc.recv(4096)
                    if not data:
                        print("Connection closed by the remote host.")
                        break
                    self.event.emit('raw', data)

                except OSError as e:
                    print(e)
                    break
            else:
                if self.config.nodataTimeout and self.config.nodataTimeout > 0:
                    print("No data received for %s seconds, quiting..." % str(self.config.nodataTimeout))
                    break

        self.irc.close()
        exit(1)

    def join(self, channel: str) -> None:
        buffer = "JOIN %s\r\n" % channel
        self.irc.send(buffer.encode('utf-8'))

    def setUser(self, user: str, realname: str) -> None:
        command = "USER %s 0 * :%s\r\n" % (user, realname)
        self.irc.send(command.encode('utf-8'))

    def setNick(self, nick: str) -> None:
        command = "NICK %s\r\n" % nick
        self.irc.send(command.encode('utf-8'))

    def nickServIdentify(self, fmt: str, password: str) -> None:
        if not password:
            return
        formatted = fmt % password
        command = "PRIVMSG %s\r\n" % formatted
        self.irc.send(command.encode('utf-8'))

    def handle_raw_message(self, data: bytes) -> None:
        self._recv_buffer += data.decode('utf-8')

        while '\r\n' in self._recv_buffer:
            line, self._recv_buffer = self._recv_buffer.split('\r\n', 1)
            if line:
                message, prefix, command, params, trailing = self.parse_message(line)

                if command == 'PING':
                    print('PING', trailing)
                    self.sendRaw('PONG ' + trailing + '\r\n')

                if command == '376' or command == '422':
                    self.event.emit('connected', 'End of /MOTD command.')

    def parse_message(self, data: str) -> tuple:
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
        actualMessage = ' '.join(params[1:]) if len(params) > 1 else None
        if actualMessage and actualMessage.startswith(':'):
            actualMessage = actualMessage[1:]

        self.event.emit('message',
                        Message(data, prefix, command, params, trailing, messageFrom, messageTo, actualMessage))

        return data, prefix, command, params, trailing
