import sys,requests,getpass,urllib2,base64
from lxml import etree

class DaiquiriAdmin():
    def __init__(self, baseUrl, username=None, password=None):
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

    def get(self, path, json=True):
        url = self.baseUrl + path

        username = self.getUsername()
        password = self.getPassword()

        if json:
            headers = {'Accept': 'application/json'}
        else:
            headers = {}

        r = requests.get(url,auth=(username,password),headers=headers)
        r.raise_for_status()
        
        if json:
            try:
                return r.json()
            except ValueError:
                sys.exit(r.text)
        else:
            return r.text

    def post(self, path, data, json=True):
        url = self.baseUrl + path

        username = self.getUsername()
        password = self.getPassword()

        if json:
            headers = {'Accept': 'application/json'}
        else:
            headers = {}

        r = requests.post(url,auth=(username,password),headers=headers,data=data)
        r.raise_for_status()

        if json:
            try:
                return r.json()
            except ValueError:
                sys.exit(r.text)
        else:
            return r.text

    def delete(self, path, json=True):
        url = self.baseUrl + path

        username = self.getUsername()
        password = self.getPassword()

        if json:
            headers = {'Accept': 'application/json'}
        else:
            headers = {}

        r = requests.delete(url,auth=(username,password),headers=headers)
        r.raise_for_status()

        if json:
            try:
                return r.json()
            except ValueError:
                sys.exit(r.text)
        else:
            return r.text

    def download(self, url, filename, chunkSizeKB=1024, callback=None):

        username = self.getUsername()
        password = self.getPassword()

        authString = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

        request = urllib2.Request(url)
        request.add_header("Authorization", "Basic %s" % authString)
        handler = urllib2.urlopen(request)

        chunkSize = int(chunkSizeKB * 1024)

        if handler.headers.get('content-length') is not None:
            fileSize = handler.headers.get('content-length')
        else:
            fileSize = None

        #write the data to file
        fileRead = 0
        with open(filename, 'wb') as filePtr:
            for chunk in iter(lambda: handler.read(chunkSize), ''):
                fileRead += len(chunk)
                filePtr.write(chunk)

                if callback is not None:
                    callback(fileSize, fileRead)

        return True

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
                if cols != 'options':
                    user[col] = value
            users.append(user)

        return users

    def fetchUser(self, userId):
        # fetch the cols
        response = self.get('/auth/user/show/id/%s' % userId)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['row']

    def fetchPassword(self, userId, type='default'):
        # fetch the cols
        response = self.get('/auth/password/show/id/%s/type/%s' % (userId,type))
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])
        else:
            return response['data']

    def storeUser(self, user):
        user['newPassword'] = user['password']
        user['confirmPassword'] = user['password']
        user['status_id'] = 1
        del user['password']

        response = self.post('/auth/user/create', user)
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def storeDetail(self, userId, key, value):
        response = self.post('/auth/details/create/id/%s' % userId, {'key': key, 'value': value})
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def removeDetail(self, userId, key):
        response = self.post('/auth/details/delete/id/%s' % userId, {'key': key})
        if response['status'] != 'ok':
            raise DaiquiriException(response['errors'])

    def activateUser(self, userId):
        response = self.post('/auth/registration/activate/id/%s' % userId, {'submit': True})
        if response['status'] != 'ok':
            print response
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

    def fetchUwsJobs(self):
        response = self.get('/uws/query/', json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        xlink = '{http://www.w3.org/1999/xlink}'

        jobs = []
        for node in root.findall(ns + 'jobref'):
            jobs.append({
                'table': node.attrib['id'],
                'id': node.attrib[xlink + 'href'].split('/')[-1],
                'status': node.find(ns + 'phase').text
            })

        return jobs

    def submitUws(self, sql, tablename=None):
        data = {'query': sql}

        if tablename:
            data['table'] = tablename

        response = self.post('/uws/query/', data, json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        jobId = root.find(ns + 'jobId').text
        
        response = self.post('/uws/query/' + jobId, {"phase": "run"}, json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'

        for node in root.find(ns + 'parameters').findall(ns + 'parameter'):
            if node.attrib['id'] == 'table':
                return node.text

    def deleteUwsJob(self, jobId):
        self.delete('/uws/query/' + jobId, json=False)

    def fetchUwsResults(self, jobId, format):
        response = self.get('/uws/query/' + jobId, json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        xlink = '{http://www.w3.org/1999/xlink}'

        for node in root.find(ns + 'parameters').findall(ns + 'parameter'):
            if node.attrib['id'] == 'table':
                name = node.text

        for node in root.find(ns + 'results').findall(ns + 'result'):

            if format == node.attrib['id']:
                url = node.attrib[xlink + 'href']
                self.download(url,name + '.' + format)

        # return jobs

class DaiquiriException(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return repr(self.errors)
