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

class CB_ZD_Create_Authentication_Server(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyCreateAuthenticationServer()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._updateCarrierBag()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'auth_ser_cfg_list': [],
                    }
        self.conf.update(conf)
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyCreateAuthenticationServer(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            cfg_server_info_list = lib.zd.aaa.get_auth_server_info_list(self.zd)
            cfg_server_name_list = [tmp['name'] for tmp in cfg_server_info_list]

            for server_cfg in self.conf['auth_ser_cfg_list']:
                if server_cfg['server_name'] in cfg_server_name_list:
                    lib.zd.aaa.edit_server(self.zd, server_cfg['server_name'], server_cfg)
                    self.passmsg = 'The authentication servers %s are edited successfully' % self.conf['auth_ser_cfg_list']
                else:
                    lib.zd.aaa.create_server(self.zd, **server_cfg)
                    self.passmsg = 'The authentication servers %s are created successfully' % self.conf['auth_ser_cfg_list']

            logging.debug(self.passmsg)

        except Exception, e:
            self.errmsg = '[Authentication server creating failed] %s' % e.message
            logging.debug(self.errmsg)

    def _updateCarrierBag(self):
        self.carrierbag['existing_authentication_sers'] = lib.zd.aaa.get_auth_server_info_list(self.zd)
