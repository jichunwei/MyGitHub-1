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
from RuckusAutoTest.components import NetgearSwitchRouter


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Init_Wired_Mesh_Network_Test_Environment(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cleanupNonDefaultConfigOnZD()
        self._cfgAuthenticationServer()

    def test(self):
        self._settingVLANOnAllAPsPort()
        self._turnAllAPsPortOn()
        self._verifyNumberAPs()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'expected_number_ap': 6,
                     'default_ap_ports_vlan_cfg':  """
                                                   interface range 1/0/1-1/0/12
                                                   vlan participation include 301
                                                   vlan pvid 301
                                                   vlan participation include 2
                                                   vlan tagging 2
                                                   vlan participation include 302
                                                   vlan tagging 302
                                                   vlan participation include 3677
                                                   vlan tagging 3677
                                                   vlan participation exclude 110
                                                   no vlan tagging 110
                                                   vlan participation exclude 777
                                                   """,
                    'check_status_timeout': 180,
                    'waiting_time': 1000,
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.l3switch = NetgearSwitchRouter.NetgearSwitchRouter(self.testbed.components['L3Switch'].conf)

        self.errmsg = ''
        self.passmsg = ''

    def _verifyNumberAPs(self):
        # verify all connected APs and that the number of connected APs is as expected
        logging.info('Check the number of connected APs')
        self.all_ap_information = lib.zd.ap.get_all_ap_info(self.zd)
        if len(self.all_ap_information) != self.conf['expected_number_ap']:
            errmsg = 'The current number connected APs is %s instead of %s'
            self.errmsg = errmsg % (len(self.all_ap_information), self.conf['expected_number_ap'])
            logging.debug(self.errmsg)
            return

        all_aps_connection_status = {}
        for ap in self.all_ap_information.keys():
            all_aps_connection_status[ap] = self.all_ap_information[ap]['status']
        self.carrierbag['existing_aps_connection_status'] = all_aps_connection_status
        self.passmsg = 'There are %s connected APs as expected' % len(self.all_ap_information)

    def _turnAllAPsPortOn(self):
        self.testbed.enable_ap_switch_ports()

    def _settingVLANOnAllAPsPort(self):
        self.l3switch.do_cfg(self.conf['default_ap_ports_vlan_cfg'])

    def _cleanupNonDefaultConfigOnZD(self):
        logging.info("Remove all configuration on the Zone Director")
        self.zd.remove_all_cfg()

    def _cfgAuthenticationServer(self):
        logging.info('Configure the external server on Zone Director')
        lib.zd.aaa.create_server(self.zd, **self.conf['auth_server_info'])
