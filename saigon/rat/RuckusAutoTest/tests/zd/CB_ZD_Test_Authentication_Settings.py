# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
verify the expected auth server in zd
by west
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Test_Authentication_Settings(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        for param in self.parameter_list:
            if not lib.zd.aaa.test_authentication_settings(**param):
                self.errmsg += 'param test failed %s'%param
                
        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zd = self.testbed.components['ZoneDirector']  
        self.conf = {'invalid_username':'',
                     'invalid_password':'',
                     'server_name':'',
                     'server_type':'',
                     'user_name':'',
                     'password':'',
                     'unreachable_server_name':'',
                     'unreachable_server_type':'',
                     'unreachable_user_name':'',
                     'unreachable_password':'',
                    }
        self.conf.update(conf)
        parameter_list=[]
        if self.conf.get('server_name'):
            param={'zd':self.zd,
                   'server':self.conf['server_name'],
                   'user':self.conf['user_name'],
                   'password':self.conf['password'],
                   'server_type':self.conf['server_type'],
                   'expected_result':'success'
                   }
            parameter_list.append(param)
            
        if self.conf.get('invalid_username'):
            param={'zd':self.zd,
                   'server':self.conf['server_name'],
                   'user':self.conf['invalid_username'],
                   'password':self.conf['invalid_password'],
                   'server_type':self.conf['server_type'],
                   'expected_result':'fail'
                   }
            parameter_list.append(param)
            
        if self.conf.get('unreachable_server_name'):
            param={'zd':self.zd,
                   'server':self.conf['unreachable_server_name'],
                   'user':self.conf['unreachable_user_name'],
                   'password':self.conf['unreachable_password'],
                   'server_type':self.conf['unreachable_server_type'],
                   'expected_result':'unreachable'
                   }
            parameter_list.append(param)
        self.parameter_list=parameter_list
        self.errmsg = ''
        self.passmsg = ''
