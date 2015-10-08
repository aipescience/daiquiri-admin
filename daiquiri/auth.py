from daiquiri.exceptions import DaiquiriException


class Auth():
    def __init__(self, connection):
        self.connection = connection

    def fetch_users(self):
        # fetch the cols
        response = self.connection.get('/auth/user/cols')
        cols = [row['name'] for row in response['cols']]

        # fetch the rows
        response = self.connection.get('/auth/user/rows')

        # return user array
        users = []
        for row in response['rows']:
            user = {}
            for col, value in zip(cols, row['cell']):
                if cols != 'options':
                    user[col] = value
            users.append(user)

        return users

    def fetch_user(self, user_id):
        # fetch the cols
        response = self.connection.get('/auth/user/show/id/%s' % user_id)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['row']

    def fetch_user_by_username(self, username):
        for user in self.fetch_users():
            if user['username'] == username:
                return self.fetch_user(user['id'])

    def fetch_user_by_email(self, email):
        for user in self.fetch_users():
            if user['email'] == email:
                return self.fetch_user(user['id'])

    def fetch_password(self, user_id, type='default'):
        # fetch the cols
        response = self.connection.get('/auth/password/show/id/%s/type/%s' % (user_id, type))
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['data']

    def store_user(self, user):
        user['newPassword'] = user['password']
        user['confirmPassword'] = user['password']
        user['status_id'] = 1
        del user['password']

        response = self.connection.post('/auth/user/create', user)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def store_detail(self, user_id, key, value):
        response = self.connection.post('/auth/details/create/id/%s' % user_id, {'key': key, 'value': value})
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def remove_detail(self, user_id, key):
        response = self.connection.post('/auth/details/delete/id/%s' % user_id, {'key': key})
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def activate_user(self, user_id):
        response = self.connection.post('/auth/registration/activate/id/%s' % user_id, {'submit': True})
        if response['status'] != 'ok':
            print response
            raise DaiquiriException(response['errors'])
