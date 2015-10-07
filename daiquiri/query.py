from daiquiri.exceptions import DaiquiriException

class Query():
    def __init__(self, connection):
        self.connection = connection