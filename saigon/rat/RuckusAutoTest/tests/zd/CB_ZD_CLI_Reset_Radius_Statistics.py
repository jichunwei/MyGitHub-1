'''
Description:
    This script is used to reset the Radius Statistic information.

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

class CB_ZD_CLI_Reset_Radius_Statistics(Test):

    def config(self, conf):
        self._init_test_params(conf)
    
    def test(self):            
        
        reset_radius_errmsg = aaa.reset_radius_statistics(self.zdcli,self.server_name)
        if reset_radius_errmsg :
            self.returnResult('FAIL', reset_radius_errmsg)
        else:
            return self.returnResult('PASS', 'the radius statistics is reset for server:%s' % self.server_name)
  
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