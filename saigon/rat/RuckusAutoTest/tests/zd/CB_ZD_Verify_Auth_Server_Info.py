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

class CB_ZD_Verify_Auth_Server_Info(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyAuthenticationServerInfo()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'expected_authentication_sers':{},
                    }
        self.conf['expected_authentication_sers'].update(conf)
        self.expected_authen_ser_info = self.conf['expected_authentication_sers']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyAuthenticationServerInfo(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        error_server_list = []
        server_info_on_zd = lib.zd.aaa.get_auth_server_info(self.zd)
        logging.info('servers on zd:%s'%server_info_on_zd)
        logging.info('expected servers:%s'%self.expected_authen_ser_info)
        for server in self.expected_authen_ser_info:
            if (server not in server_info_on_zd) or (server_info_on_zd[server]!=self.expected_authen_ser_info[server]):
                error_server_list.append(server)
        if error_server_list:
            self.errmsg = 'The authentication servers %s are not shown on the WebUI correctly' % error_server_list
            logging.debug(self.errmsg)
            return

        self.passmsg = 'The authentication servers %s are shown on WebUI correctly' % self.expected_authen_ser_info
