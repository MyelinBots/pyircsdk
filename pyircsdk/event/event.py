class Event:
    def __init__(self):
        self.listeners = {}

    def emit(self, name, data):
        if name in self.listeners:
            for callback in self.listeners[name]:
                callback(data)

    def on(self, name, callback):
        if name not in self.listeners:
            self.listeners[name] = []
        self.listeners[name].append(callback)

    def remove(self, name, callback):
        if name in self.listeners:
            try:
                self.listeners[name].remove(callback)
            except ValueError:
                pass

    def remove_all(self, name):
        if name in self.listeners:
            self.listeners[name] = []
