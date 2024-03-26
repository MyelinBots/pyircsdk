# pyIRCSDK

pyIRCSDK is a Python library for creating IRC bots and clients. It is designed to provide granular access to raw mesages
and to provide an event emitter like interface for handling messages.

## Installation

```bash
pip install pyIRCSDK
```

## Usage

```python
from pyIRCSDK import IRCClient

client = IRCClient("irc.freenode.net", 6667, "pyIRCSDK", "pyIRCSDK")
client.event.on("message", lambda message: print(message))
client.event.on("connected", lambda: client.send("JOIN #pyIRCSDK"))
client.event.on("raw", lambda message: print(message))
client.connect()

```

More event to come soon:
* connected
* disconnected
* join
* part
* kicked
* message
* raw
