from daiquiri.exceptions import DaiquiriException


class Data():
    def __init__(self, connection, dryrun=False):
        self.connection = connection
        self.dryrun = dryrun

    def fetch_databases(self):
        response = self.connection.get('/data/databases/')
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['databases']

    def update_table(self, table_id, table):
        if not self.dryrun:
            response = self.connection.get('/data/tables/show/id/%s' % table_id)
            data = {
                'database_id': response['row']['database_id'],
                'order': response['row']['order'],
                'name': response['row']['name'],
                'description': response['row']['description'],
                'publication_role_id': response['row']['publication_role_id']
            }
            data.update(table)

            response = self.connection.post('/data/tables/update/id/%s' % table_id, data)
            if response['status'] != 'ok':
                raise DaiquiriException(response['errors'])

    def update_column(self, column_id, column):
        if not self.dryrun:
            response = self.connection.get('/data/columns/show/id/%s' % column_id)
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

            response = self.connection.post('/data/columns/update/id/%s' % column_id, data)
            if response['status'] != 'ok':
                raise DaiquiriException(response['errors'])

    def store_function(self, function):
        if not self.dryrun:
            response = self.connection.post('/data/functions/create', function)
            if response['status'] != 'ok':
                raise DaiquiriException(response['errors'])
