import re
import sys
from urllib.request import urlopen

from bs4 import BeautifulSoup
from pyircsdk import Module


class URLParse(Module):
    def __init__(self, irc):
        super().__init__(irc, "", "")

    def handleCommand(self, message, command):
        if message.command == 'PRIVMSG':
            # if url is found in message
            if 'http' in message.message:
                # get the url with regex
                url = re.search("(?P<url>https?://[^\s]+)", message.message).group("url")


                soup = BeautifulSoup(urlopen(url))

                title = soup.title.string
                self.irc.privmsg(message.messageTo, "Title: %s" % title)
