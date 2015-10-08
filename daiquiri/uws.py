import fnmatch
from lxml import etree

from daiquiri.exceptions import DaiquiriException


class UWS():
    def __init__(self, connection):
        self.connection = connection
        self.ns = '{http://www.ivoa.net/xml/UWS/v1.0}'
        self.xlink = '{http://www.w3.org/1999/xlink}'

    def fetch_jobs(self):
        response = self.connection.get('/uws/query/', json=False)

        # remove first line and parse xml
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)

        jobs = []
        for node in root.findall(self.ns + 'jobref'):
            jobs.append({
                'name': node.attrib['id'],   # This is actually the job's name, not the 'intended' table name in parameter list. Maybe rename to 'name'?
                'id': node.attrib[self.xlink + 'href'].split('/')[-1],
                'status': node.find(self.ns + 'phase').text
            })

        return jobs

    def submit(self, sql, tablename=None):
        data = {'query': sql}

        if tablename:
            data['table'] = tablename

        response = self.connection.post('/uws/query/', data, json=False)

        # remove first line and parse xml
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)

        response = self.connection.post('/uws/query/' + jobId, {"phase": "run"}, json=False)

        # remove first line
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)


        for node in root.find(self.ns + 'parameters').findall(self.ns + 'parameter'):
            if node.attrib['id'] == 'table':
                return jobId, node.text

    def delete_job(self, jobId):
        self.connection.delete('/uws/query/' + jobId, json=False)

    def fetch_results(self, jobId, format):
        response = self.connection.get('/uws/query/' + jobId, json=False)

        # remove first line and parse xml
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)

        for node in root.find(self.ns + 'parameters').findall(self.ns + 'parameter'):
            if node.attrib['id'] == 'table':
                name = node.text

        for node in root.find(self.ns + 'results').findall(self.ns + 'result'):

            if format == node.attrib['id']:
                url = node.attrib[self.xlink + 'href']
                self.connection.download(url,name + '.' + format)

    def fetch_result_url(self, jobId, format):
        '''Get url of result for given jobId and format'''

        response = self.connection.get('/uws/query/' + jobId + 'results/', json=False)

        # remove first line and parse xml
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)

        for node in root.find(self.ns + 'results').findall(self.ns + 'result'):

            if format == node.attrib['id']:
                url = node.attrib[self.xlink + 'href']

        return url

    def get_job(self, jobId):
        '''Get details of the job with given jobId'''

        response = self.connection.get('/uws/query/' + jobId , json=False)

        # remove first line and parse xml
        string = '\n'.join(response.split('\n')[1:])
        root = etree.XML(string)

        job = {}
        job['id'] = root.find(ns + 'jobId').text
        job['status'] = root.find(ns + 'phase').text

        if root.find(ns + 'errorSummary') is not None:
            node = root.find(self.ns + 'errorSummary').find(self.ns + 'message')
            job['errors'] = node.text

        for node in root.find(self.ns + 'parameters').findall(self.ns + 'parameter'):
            if node.attrib['id'] == 'table':
                job['table'] = node.text

        return job

    def get_jobs_by_name_and_phase(self, jobname, phase):
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

        jobs = self.fetch_jobs()

        joblist = []
        for job in jobs:
            if fnmatch.fnmatch(job['name'], jobname):
                if fnmatch.fnmatch(job['status'], phase):
                    joblist.append(job)

        return joblist
