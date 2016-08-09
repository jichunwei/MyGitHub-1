# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    remove one aaa server from ZD

"""

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Remove_Authentication_Server(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyRemoveAuthenticationServer()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._updateCarrierBag()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'auth_ser_name_list': [],
                    }
        self.conf.update(conf)
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyRemoveAuthenticationServer(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            for name in self.conf['auth_ser_name_list']:
                lib.zd.aaa.del_server(self.zd,name)
            self.passmsg = 'The authentication servers %s is removed created successfully' % self.conf['auth_ser_name_list']
            logging.debug(self.passmsg)

        except Exception, e:
            self.errmsg = '[Authentication server remove failed] %s' % e.message
            logging.debug(self.errmsg)

    def _updateCarrierBag(self):
        pass