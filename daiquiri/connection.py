import sys
import requests
import urllib2
import base64
import getpass


class Connection():
    def __init__(self, baseUrl, username=None, password=None):
        self.baseUrl = baseUrl
        self.username = username
        self.password = password

    def get(self, path, json=True):
        url = self.baseUrl + path

        username = self.get_username()
        password = self.get_password()

        if json:
            headers = {'Accept': 'application/json'}
        else:
            headers = {}

        r = requests.get(url, auth=(username, password), headers=headers)
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

        username = self.get_username()
        password = self.get_password()

        if json:
            headers = {'Accept': 'application/json'}
        else:
            headers = {}

        r = requests.post(url, auth=(username, password), headers=headers, data=data)
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

        username = self.get_username()
        password = self.get_password()

        if json:
            headers = {'Accept': 'application/json'}
        else:
            headers = {}

        r = requests.delete(url, auth=(username, password), headers=headers)
        r.raise_for_status()

        if json:
            try:
                return r.json()
            except ValueError:
                sys.exit(r.text)
        else:
            return r.text

    def download(self, url, filename, chunkSizeKB=1024, callback=None):

        username = self.get_username()
        password = self.get_password()

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

    def get_username(self):
        if not self.username:
            self.username = getpass.getuser()

        return self.username

    def get_password(self):
        if not self.password:
            self.password = getpass.getpass()

        return self.password
