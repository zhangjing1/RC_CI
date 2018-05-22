"""
This script acts as a client to confluence, connects to confluence and create
pages
"""
# !/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from requests_kerberos import HTTPKerberosAuth
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class ConfluenceClientForUpdatePage:
    """ A conflence component used to connect to confluence and perform
    confluence related tasks
    """
    def __init__(self, confluence_space, confluence_page_title,
                 confluence_url, username=None, password=None,
                 auth_type='basic'):
        """ Returns confluence client object
        :param string confluence_space : space to be used in confluence
        :param strinf confluence_page_title : Title of page to be created in
        confluence
        :param string confluence_url : url to connect confluence
        :param string username : optional username for basic auth
        :param string password : optional password for basic auth
        :param string auth_type : indicate auth scheme (basic/kerberos)
        """
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.confluence_space = confluence_space
        self.confluence_page_title = confluence_page_title
        self.confluence_url = confluence_url
        self.username = username
        self.password = password
        self.authtype = auth_type
        self._req_kwargs = None
    @property
    def req_kwargs(self):
        """ Set the key-word arguments for python-requests depending on the
        auth type. This code should run on demand exactly once, which is
        why it is a property.
        :return dict _req_kwargs: dict with the right options to pass in
        """
        if self._req_kwargs is None:
            if self.authtype == 'kerberos':
                # First we get a cookie from the "step" site, which is just
                # an nginx proxy that is kerberos enabled.
                step_url = self.confluence_url + '/step-auth-gss'
                conf_resp = requests.get(step_url, auth=self.get_auth_object())
                conf_resp.raise_for_status()
                # Going forward, we just pass in "cookies", no need to provide
                # an auth object anymore. In fact if we do, it'll get
                # preferred and fail since the service itself is not kerberos
                # enabled.
                self._req_kwargs = {'cookies': conf_resp.cookies, 'verify': False }
            elif self.authtype == 'basic':
                self._req_kwargs = {'auth': self.get_auth_object(), 'verify': False }
        return self._req_kwargs

    def update_page(self, page_info, html):
        """
        Updates the page with html
        the function will get the info from page_info first, like page_id, page_version
        :param string page_info: the info of the page
        :param string html : html content of the page
        :return json conf_resp: response from the confluence
        """

        page_id=page_info['id']
        version=page_info['version']
        title=page_info['title']

        confluence_rest_url = self.confluence_url + "/rest/api/content/" +\
            page_id

        updated_page_version = int(version) + 1
        data = {
            'id': str(page_id),
            'type': 'page',
            'title': title,
            'version': {
                'number': updated_page_version},
            'body': {
                'storage': {
                    'representation': 'storage',
                    'value': html}}}
        resp = requests.put(confluence_rest_url, json=data, **self.req_kwargs)
        resp.raise_for_status()
        return resp.json()

    def get_auth_object(self):
        """Returns Auth object based on auth type
        :return : Auth Object
        """
        if self.authtype == 'kerberos':
            # I'm not sure disabling auth is a good idea, but most of the examples I've
            # seen internally do this. Probably makes me part of the problem.
            return HTTPKerberosAuth(mutual_authentication=False)
        elif self.authtype == "basic":
            return HTTPBasicAuth(self.username, self.password)