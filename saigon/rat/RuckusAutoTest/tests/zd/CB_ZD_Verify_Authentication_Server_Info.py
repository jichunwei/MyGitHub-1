# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Verify_Authentication_Server_Info(Test):
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
        self.conf = {'expected_authentication_sers': [],
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        if self.carrierbag.get('existing_authentication_sers'):
            self.expected_authen_ser_info = self.carrierbag['existing_authentication_sers']
        elif self.carrierbag.get('backup_info') and self.carrierbag['backup_info'].get('existing_authentication_sers'):
            self.expected_authen_ser_info = self.carrierbag['backup_info']['existing_authentication_sers']
        else:
            self.expected_authen_ser_info = self.conf['expected_authentication_sers']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyAuthenticationServerInfo(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        error_server_list = []
        server_info_list_on_zd = lib.zd.aaa.get_auth_server_info_list(self.zd)
        for server_info in self.expected_authen_ser_info:
            if server_info not in server_info_list_on_zd:
                error_server_list.append(server_info)
        if error_server_list:
            self.errmsg = 'The authentication servers %s are not shown on the WebUI' % error_server_list
            logging.debug(self.errmsg)
            return

        self.passmsg = 'The authentication servers %s are shown on WebUI correctly' % server_info_list_on_zd
