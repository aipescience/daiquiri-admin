from daiquiri.exceptions import DaiquiriException


class Query():
    def __init__(self, connection):
        self.connection = connection

    def fetch_queries(self, year, month):
        response = self.connection.post('/query/jobs/export/', {
            'year': year,
            'month': month
        })

        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['rows']
