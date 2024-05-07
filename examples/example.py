import sys

from modules.hello.hello import HelloModule
from modules.quit.quit import QuitModule
from modules.urlparse.urlparse import URLParse
from pyircsdk import IRCSDKConfig, IRCSDK, Module

irc = IRCSDK(IRCSDKConfig('irc.rizon.net',
                          6667,
                          'pyircsdk',
                          '#toolbot',
                          'pyircsdk',
                          'pyircsdk made by nyankochan'
                          ))

helloModule = HelloModule(irc)
quitModule = QuitModule(irc)
urlParseModule = URLParse(irc)
quitModule.startListening()
helloModule.startListening()
urlParseModule.startListening()

irc.connect(None)
