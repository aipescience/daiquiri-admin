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
        
        try:
            return r.json()
        except ValueError:
            sys.exit(r.text)

    def post(self, path, data):
        url = self.baseUrl + path

        username = self.getUsername()
        password = self.getPassword()
        headers = {'Accept': 'application/json'}

        r = requests.post(url,auth=(username,password),headers=headers,data=data)
        r.raise_for_status()

        try:
            return r.json()
        except ValueError:
            sys.exit(r.text)

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

    def fetchPassword(self,userId,type):
        # fetch the cols
        response = self.get('/auth/password/show/id/%s/type/%s' % (userId,type))
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['row']

    def storeUser(self, user):
        user['newPassword'] = user['password']
        user['confirmPassword'] = user['password']
        user['status_id'] = 1
        del user['password']

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
            'table_id': response['row']['table_id'],
            'order': response['row']['order'],
            'name': response['row']['name'],
            'type': response['row']['type'],
            'unit': response['row']['unit'],
            'ucd': response['row']['ucd'],
            'description': response['row']['description']
        }
        data.update(column)

        response = self.post('/data/columns/update/id/%s' % columnId, data)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def storeFunction(self, function):
        response = self.post('/data/functions/create', function)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

class DaiquiriException(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return repr(self.errors)
