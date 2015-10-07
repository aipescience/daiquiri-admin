import fnmatch
from lxml import etree

from daiquiri.exceptions import DaiquiriException

class UWS():
    def __init__(self, connection):
        self.connection = connection

    def fetchJobs(self):
        response = self.connection.get('/uws/query/', json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        xlink = '{http://www.w3.org/1999/xlink}'

        jobs = []
        for node in root.findall(ns + 'jobref'):
            jobs.append({
                'name': node.attrib['id'],   # This is actually the job's name, not the 'intended' table name in parameter list. Maybe rename to 'name'?
                'id': node.attrib[xlink + 'href'].split('/')[-1],
                'status': node.find(ns + 'phase').text
            })

        return jobs

    def submit(self, sql, tablename=None):
        data = {'query': sql}

        if tablename:
            data['table'] = tablename

        response = self.connection.post('/uws/query/', data, json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        jobId = root.find(ns + 'jobId').text

        response = self.connection.post('/uws/query/' + jobId, {"phase": "run"}, json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])

        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'

        for node in root.find(ns + 'parameters').findall(ns + 'parameter'):
            if node.attrib['id'] == 'table':
                return jobId, node.text

    def deleteJob(self, jobId):
        self.connection.delete('/uws/query/' + jobId, json=False)

    def fetchResults(self, jobId, format):
        response = self.connection.get('/uws/query/' + jobId, json=False)

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
                self.connection.download(url,name + '.' + format)

        # return url


    def fetchResultUrl(self, jobId, format):
        '''Get url of result for given jobId and format'''

        response = self.connection.get('/uws/query/' + jobId + 'results/', json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        xlink = '{http://www.w3.org/1999/xlink}'

        for node in root.find(ns + 'results').findall(ns + 'result'):

            if format == node.attrib['id']:
                url = node.attrib[xlink + 'href']

        return url

    def getJob(self, jobId):
        '''Get details of the job with given jobId'''

        response = self.connection.get('/uws/query/' + jobId , json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)
        ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        xlink = '{http://www.w3.org/1999/xlink}'

        job = {}
        job['id'] = root.find(ns + 'jobId').text
        job['status'] = root.find(ns + 'phase').text

        if root.find(ns + 'errorSummary') is not None:
            node = root.find(ns + 'errorSummary').find(ns + 'message')
            job['errors'] = node.text

        for node in root.find(ns + 'parameters').findall(ns + 'parameter'):
            if node.attrib['id'] == 'table':
                job['table'] = node.text

        return job

    def getJobsByNameAndPhase(self, jobname, phase):
        '''
        Get jobIds matching given job name (pattern) and phase
        Uses fnmatch, so table name pattern examples are:
        *result-*, validate-[1-3]*
        '''
        # NOTE: Usually, job name = result table name, unless there was
        # an error when submitting the query. This routine *won't* return
        # all jobs whose *intended* table name matches the given name,
        # only those which really have this name as their jobname
        # (id-attribute in jobref) are returned.

        jobs = self.fetchJobs()

        joblist = []
        for job in jobs:
            if fnmatch.fnmatch(job['name'], jobname):
                if fnmatch.fnmatch(job['status'], phase):
                    joblist.append(job)

        return joblist
