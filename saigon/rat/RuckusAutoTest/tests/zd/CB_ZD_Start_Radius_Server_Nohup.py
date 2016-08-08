
"""
Description: Start radius server in the background by nohup option
"""

import os
import logging
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_Start_Radius_Server_Nohup(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf   = conf.copy()
        self.server = self.testbed.components['LinuxServer']
        self.passmsg = ''

    def test(self):
        try:
            self.server.start_radius_server_output_to_file()
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        self.passmsg = 'Start radius server with nohup option successfully'
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
