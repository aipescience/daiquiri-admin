import sys,requests,getpass

class DaiquiriAdmin():
    def __init__(self, baseUrl, username=None, password=None):
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

    def get(self, path):
        url = self.baseUrl + path

        username = self.getUsername()
        password = self.getPassword()
        headers = {'Accept': 'application/json'}

        r = requests.get(url,auth=(username,password),headers=headers)
        r.raise_for_status()
        return r.json()

    def post(self, path, data):
        url = self.baseUrl + path

        username = self.getUsername()
        password = self.getPassword()
        headers = {'Accept': 'application/json'}

        r = requests.post(url,auth=(username,password),headers=headers,data=data)
        r.raise_for_status()

        return r.json()


    def getUsername(self):
        if not self.username:
            self.username = getpass.getuser()

        return self.username

    def getPassword(self):
        if not self.password:
            self.password = getpass.getpass()

        return self.password

    def fetchUsers(self):
        # fetch the cols
        response = self.get('/auth/user/cols')
        cols = [row['name'] for row in response['cols']]

        # fetch the rows
        response = self.get('/auth/user/rows')

        # return user array
        users = []
        for row in response['rows']:
            user = {}
            for col,value in zip(cols,row['cell']):
                user[col] = value
            users.append(user)

        return users

    def storeUser(self, user):
        response = self.post('/auth/user/create', user)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def fetchDatabases(self):
        response = self.get('/data/databases/')
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['databases']

    def updateColumn(self, columnId, column):
        response = self.get('/data/columns/show/id/%s' % columnId)
        data = {
            'table_id': response['data']['table_id'],
            'position': response['data']['position'],
            'name': response['data']['name'],
            'type': response['data']['type'],
            'unit': response['data']['unit'],
            'ucd': response['data']['ucd'],
            'description': response['data']['description']
        }
        data.update(column)

        response = self.post('/data/columns/update/id/%s' % columnId, data)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

class DaiquiriException(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return repr(self.errors)
