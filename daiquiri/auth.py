from daiquiri.exceptions import DaiquiriException

class Auth():
    def __init__(self, connection):
        self.connection = connection

    def fetchUsers(self):
        # fetch the cols
        response = self.connection.get('/auth/user/cols')
        cols = [row['name'] for row in response['cols']]

        # fetch the rows
        response = self.connection.get('/auth/user/rows')

        # return user array
        users = []
        for row in response['rows']:
            user = {}
            for col,value in zip(cols,row['cell']):
                if cols != 'options':
                    user[col] = value
            users.append(user)

        return users

    def fetchUser(self, userId):
        # fetch the cols
        response = self.connection.get('/auth/user/show/id/%s' % userId)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['row']

    def fetchUserByUsername(self, username):
        for user in self.fetchUsers():
            if user['username'] == username:
                return self.fetchUser(user['id'])

    def fetchUserByEmail(self, email):
        for user in self.fetchUsers():
            if user['email'] == email:
                return self.fetchUser(user['id'])

    def fetchPassword(self, userId, type='default'):
        # fetch the cols
        response = self.connection.get('/auth/password/show/id/%s/type/%s' % (userId,type))
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['data']

    def storeUser(self, user):
        user['newPassword'] = user['password']
        user['confirmPassword'] = user['password']
        user['status_id'] = 1
        del user['password']

        response = self.connection.post('/auth/user/create', user)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def storeDetail(self, userId, key, value):
        response = self.connection.post('/auth/details/create/id/%s' % userId, {'key': key, 'value': value})
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def removeDetail(self, userId, key):
        response = self.connection.post('/auth/details/delete/id/%s' % userId, {'key': key})
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def activateUser(self, userId):
        response = self.connection.post('/auth/registration/activate/id/%s' % userId, {'submit': True})
        if response['status'] != 'ok':
            print response
            raise DaiquiriException(response['errors'])
