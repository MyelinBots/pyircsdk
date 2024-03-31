import sys

from examples.modules.hello.hello import HelloModule
from examples.modules.quit.quit import QuitModule
from examples.modules.urlparse.urlparse import URLParse
from pyircsdk import IRCSDKConfig, IRCSDK, Module



irc = IRCSDK(IRCSDKConfig('irc.rizon.net',
                          6667,
                          'pyircsdk',
                          '#toolbot',
                          'pyircsdk'
                          ))

helloModule = HelloModule(irc)
quitModule = QuitModule(irc)
urlParseModule = URLParse(irc)
quitModule.startListening()
helloModule.startListening()
urlParseModule.startListening()

irc.connect(None)
