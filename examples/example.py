import sys

from modules.hello.hello import HelloModule
from modules.quit.quit import QuitModule
from modules.urlparse.urlparse import URLParse
from pyircsdk import IRCSDKConfig, IRCSDK, Module

irc = IRCSDK(IRCSDKConfig(host='irc.rizon.net',
                          port=6667,
                          nick='pyircsdk2',
                          channel='#toolbot',
                          user='pyircsdk',
                          realname='pyircsdk made by nyankochan'
                          ))

helloModule = HelloModule(irc)
quitModule = QuitModule(irc)
urlParseModule = URLParse(irc)
quitModule.startListening()
helloModule.startListening()
urlParseModule.startListening()

irc.connect(None)
