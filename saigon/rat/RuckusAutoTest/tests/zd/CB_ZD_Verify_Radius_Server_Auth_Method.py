
"""
Description: To verify if ZD could authenticate to an exist radius authentication server
"""

import os
import time
import logging
import random
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_Verify_Radius_Server_Auth_Method(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.server = self.testbed.components['LinuxServer']

    def test(self):
        result, msg = ["", ""]

        file = "nohup.out"
        try:
            self.server.start_radius_server_output_to_file(file)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        if self.conf['radius_auth_method'] == 'chap':
            fail_log_list = ["Auth-Type := CHAP", "CHAP-Password", "Access-Reject"]
            succ_log_list = ["Auth-Type := CHAP", "CHAP-Password", "Access-Accept"]            
        else:
            fail_log_list = ["User-Password", "Access-Reject"]
            succ_log_list = ["User-Password", "Access-Accept"]            

        fail_reason = "%s: radius authentication method verification is incorrect(%s)"
        
        #invalid user
        auth_msg = self.zd.test_authenticate(self.conf['server_name'], self.conf['invalid_user'], self.conf['password'])
        if "Success" in auth_msg:
            return self.returnResult('FAIL', auth_msg)

        tmp = self.server.verify_radius_server_auth_method(file, fail_log_list)
        if tmp != True:
            return self.returnResult('FAIL', fail_reason % (auth_msg, "invalid user"))

        #invalid password
        auth_msg = self.zd.test_authenticate(self.conf['server_name'], self.conf['user'], self.conf['invalid_password'])
        if "Success" in auth_msg:
            return self.returnResult('FAIL', auth_msg)

        tmp = self.server.verify_radius_server_auth_method(file, fail_log_list)
        if tmp != True:
            return self.returnResult('FAIL', fail_reason % (auth_msg, "invalid password"))

        #invalid user and password
        auth_msg = self.zd.test_authenticate(self.conf['server_name'], self.conf['invalid_user'], self.conf['invalid_password'])
        if "Success" in auth_msg:
            return self.returnResult('FAIL', auth_msg)

        tmp = self.server.verify_radius_server_auth_method(file, fail_log_list)
        if tmp != True:
            return self.returnResult('FAIL', fail_reason % (auth_msg, "invalid user and password"))

        #valid user and password
        auth_msg = self.zd.test_authenticate(self.conf['server_name'], self.conf['user'], self.conf['password'])
        if "Success" in auth_msg:
            result, msg = ("PASS", "")
        else:
            result, msg = ("FAIL", auth_msg)

        tmp = self.server.verify_radius_server_auth_method(file, succ_log_list)
        if tmp != True:
            return self.returnResult('FAIL', fail_reason % (auth_msg, "valid user and password"))
       
        return (result, msg)

    def cleanup(self):
        self.server.restart_radius_server()
        pass
