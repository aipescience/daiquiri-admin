from daiquiri.exceptions import DaiquiriException

class Data():
    def __init__(self, connection):
        self.connection = connection

    def fetchDatabases(self):
        response = self.connection.get('/data/databases/')
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['databases']

    def updateColumn(self, columnId, column):
        response = self.connection.get('/data/columns/show/id/%s' % columnId)
        data = {
            'table_id': response['row']['table_id'],
            'order': response['row']['order'],
            'name': response['row']['name'],
            'type': response['row']['type'],
            'unit': response['row']['unit'],
            'ucd': response['row']['ucd'],
            'description': response['row']['description']
        }
        data.update(column)

        response = self.connection.post('/data/columns/update/id/%s' % columnId, data)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def storeFunction(self, function):
        response = self.connection.post('/data/functions/create', function)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
