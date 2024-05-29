import sys

from modules.hello.hello import HelloModule
from modules.quit.quit import QuitModule
from modules.urlparse.urlparse import URLParse
from pyircsdk import IRCSDKConfig, IRCSDK, Module

irc = IRCSDK(IRCSDKConfig(host='irc.myelinbots.com',
                          port=6697,
                          nick='pyircsdk2',
                          channel='#test',
                          ssl=True,
                          user='pyircsdk',
                          realname='pyircsdk made by nyankochan',
                          nodataTimeout=120
                          ))

helloModule = HelloModule(irc)
quitModule = QuitModule(irc)
urlParseModule = URLParse(irc)
quitModule.startListening()
helloModule.startListening()
urlParseModule.startListening()

irc.connect(None)
