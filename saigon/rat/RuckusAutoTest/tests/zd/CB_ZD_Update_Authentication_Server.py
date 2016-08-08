# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
Description:
        Update AAA Server profile.
        
    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components: ZoneDirector
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

@author: cwang@ruckuswireless.com

"""

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Update_Authentication_Server(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_parameter(conf)

    def test(self):
        self._update_aaa_server()
        if self.errmsg: return ('FAIL', self.errmsg)
        self._update_carrierbag()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_parameter(self, conf):
        self.conf = {'auth_ser_cfg': {},
                     'old_name': ''
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''

    def _update_aaa_server(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:            
            lib.zd.aaa.edit_server(self.zd, self.conf['old_name'], self.conf['auth_ser_cfg'])
            self.passmsg = 'The authentication server %s is updated successfully' % self.conf['auth_ser_cfg']
            logging.debug(self.passmsg)

        except Exception, e:
            self.errmsg = '[Authentication server creating failed] %s' % e.message
            logging.debug(self.errmsg)

    def _update_carrierbag(self):
        self.carrierbag['existing_authentication_sers'] = lib.zd.aaa.get_auth_server_info_list(self.zd)
