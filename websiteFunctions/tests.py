# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from django.urls import reverse
import json
from loginSystem.models import Administrator, ACL
from plogical.CyberCPLogFileWriter import CyberCPLogFileWriter as logging
import requests
import time
import ftp
# Create your tests here.


class TestWebsiteManagement(TestCase):
    httpClient = requests.Session()

    def MakeRequest(self, endPoint, data):
        json_data = json.dumps(data)
        path = 'https://cyberpanel.xyz:8090/%s' % (endPoint)
        result = TestWebsiteManagement.httpClient.post(path, data=json_data, verify=False)
        return json.loads(result.text)

    def MakeRequestRaw(self, path):
        result = requests.get(path)
        return str(result.text)


    def setUp(self):
        ## Verify login

        data_ret = {'username': 'admin', 'password': '1234567'}
        response = self.MakeRequest('verifyLogin', data_ret)
        self.assertEqual(response['loginStatus'], 1)

    def test_submitWebsiteCreation(self):

        ## Login

        data_ret = {'domainName': 'hello.cyberpanel.xyz', 'adminEmail': 'usman@cyberpersons.com' , 'phpSelection': 'PHP 7.1',
                    'package': 'Default', 'websiteOwner': 'admin', 'ssl': 0, 'dkimCheck': 0, 'openBasedir': 0}
        response = self.MakeRequest('websites/submitWebsiteCreation', data_ret)

        time.sleep(10)

        self.assertEqual(response['status'], 1)

        exists = 0

        if self.MakeRequestRaw('http://hello.cyberpanel.xyz').find('CyberPanel') > -1:
            exists = 1

        self.assertEqual(exists, 1)

        data_ret = {'domainName': 'hey.cyberpanel.xyz', 'adminEmail': 'usman@cyberpersons.com',
                    'phpSelection': 'PHP 7.1',
                    'package': 'Default', 'websiteOwner': 'admin', 'ssl': 0, 'dkimCheck': 0, 'openBasedir': 0}
        self.MakeRequest('websites/submitWebsiteCreation', data_ret)

        data_ret = {'domainName': 'suspend.cyberpanel.xyz', 'adminEmail': 'usman@cyberpersons.com',
                    'phpSelection': 'PHP 7.1',
                    'package': 'Default', 'websiteOwner': 'admin', 'ssl': 0, 'dkimCheck': 0, 'openBasedir': 0}
        self.MakeRequest('websites/submitWebsiteCreation', data_ret)

    def test_submitWebsiteModify(self):

        ## Login

        data_ret = {'domain': 'hey.cyberpanel.xyz', 'email': 'usman@cyberpersons.com' , 'phpVersion': 'PHP 7.3',
                    'packForWeb': 'Default', 'admin': 'admin'}

        response = self.MakeRequest('websites/saveWebsiteChanges', data_ret)

        time.sleep(5)

        self.assertEqual(response['status'], 1)

        phpInfoPath = '/home/hey.cyberpanel.xyz/public_html/info.php'
        content = """<?php

phpinfo();

?>
"""
        writeToFile = open(phpInfoPath, 'w')
        writeToFile.write(content)
        writeToFile.close()

        exists = 0

        if self.MakeRequestRaw('http://hey.cyberpanel.xyz/info.php').find('PHP 7.3') > -1:
            exists = 1

        self.assertEqual(exists, 1)


    def test_submitWebsiteDeletion(self):

        ## Login

        data_ret = {'websiteName': 'hello.cyberpanel.xyz'}

        response = self.MakeRequest('websites/submitWebsiteDeletion', data_ret)
        time.sleep(5)

        self.assertEqual(response['status'], 1)

    def test_submitWebsiteStatus(self):

        ## Suspend  check
        data_ret = {'websiteName': 'suspend.cyberpanel.xyz', 'state': 'Suspend'}

        response = self.MakeRequest('websites/submitWebsiteStatus', data_ret)

        time.sleep(5)

        self.assertEqual(response['websiteStatus'], 1)

        exists = 0

        if self.MakeRequestRaw('http://suspend.cyberpanel.xyz').find('404') > -1 or self.MakeRequestRaw('http://suspend.cyberpanel.xyz').find('Access to this resource on the server is denied!') > -1:
            exists = 1

        self.assertEqual(exists, 1)

        suspend = 0
        import os
        if os.path.exists('/usr/local/lsws/conf/vhosts/suspend.cyberpanel.xyz-suspended'):
            suspend = 1

        self.assertEqual(suspend, 1)

        ## Unsuspend  check

        data_ret = {'websiteName': 'suspend.cyberpanel.xyz', 'state': 'Unsuspend'}

        response = self.MakeRequest('websites/submitWebsiteStatus', data_ret)

        time.sleep(5)

        self.assertEqual(response['websiteStatus'], 1)

        exists = 0

        if self.MakeRequestRaw('http://suspend.cyberpanel.xyz').find('CyberPanel') > -1:
            exists = 1

        self.assertEqual(exists, 1)

        suspend = 0
        import os
        if os.path.exists('/usr/local/lsws/conf/vhosts/suspend.cyberpanel.xyz'):
            suspend = 1

        self.assertEqual(suspend, 1)





