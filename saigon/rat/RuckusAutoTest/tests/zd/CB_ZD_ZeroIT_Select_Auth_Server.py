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

class CB_ZD_ZeroIT_Select_Auth_Server(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._selectZeroITAuthenticationServer()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._updateCarrierBag()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'zero_it_auth_serv': 'Local Database',
                    }
        self.conf.update(conf)
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']

        self.errmsg = ''
        self.passmsg = ''

    def _selectZeroITAuthenticationServer(self):
        try:
            logging.info("Choose radius authentication server for Zero-IT Activation.")
            self.zd.set_zero_it_cfg(self.conf['zero_it_auth_serv'])

            self.passmsg = 'The ZeroIT authentication servers %s are selected successfully' % self.conf['zero_it_auth_serv']

            logging.debug(self.passmsg)

        except Exception, e:
            self.errmsg = '[Authentication server selection failed] %s' % e.message
            logging.debug(self.errmsg)

    def _updateCarrierBag(self):
        #self.carrierbag['existing_authentication_sers'] = lib.zd.aaa.get_auth_server_info_list(self.zd)
        pass
