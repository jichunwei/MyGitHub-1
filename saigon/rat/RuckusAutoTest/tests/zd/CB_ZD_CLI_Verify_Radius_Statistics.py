'''
Description:
    This script is used to test the Radius Statistic information.

Procedure:

    
Create on 2014-12-26
@author: zhang.jie@odc-ruckuswireless.com
'''
from RuckusAutoTest.components.lib.zdcli import aaa_servers as aaa

import logging
import time
import datetime
import os
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_ZD_CLI_Verify_Radius_Statistics(Test):

    def config(self, conf):
        self._init_test_params(conf)
    
    def test(self):            
        
        res = aaa.get_radius_statistics(self.zdcli,self.server_name)   
        if not res:
            return False,'get nothing for radius statistics information'
        
        expected_value = self.server_conf['Access Requests']
        result,msg = aaa.verify_info_radius_statistics(self.zdcli,res,self.aaa_type,expected_value)
        if result == False:
            self.returnResult('FAIL', msg)
        else :
            return self.returnResult('PASS', 'the radius statistics is as expected for server:%s' % self.server_name)

  
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = dict(server_conf = {
            'server_name': 'RADIUS',
            'server_addr': '192.168.0.252',
            'radius_auth_secret': '1234567890',
            'server_port': '1812',
            'type'       :'radius-auth',},
            )
        self.conf.update(conf)        
        self.server_conf = self.conf['server_conf']
        self.aaa_type = self.server_conf['type']
        self.server_name = self.server_conf['server_name']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''