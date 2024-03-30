
class Message:
    def __init__(self, data, prefix, command, params, trailing, messageFrom, messageTo, message):
        self.data = data
        self.prefix = prefix
        self.messageFrom = messageFrom
        self.messageTo = messageTo
        self.command = command
        self.message = message
        self.params = params
        self.trailing = trailing

    def __str__(self):
        return f'Message: {self.data}, Prefix: {self.prefix}, Message From: {self.messageFrom}, Message To: {self.messageTo}, Command: {self.command}, Params: {self.params}, Trailing: {self.trailing}'
