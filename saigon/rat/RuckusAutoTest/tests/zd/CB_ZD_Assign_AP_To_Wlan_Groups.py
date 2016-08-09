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
import time, logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Assign_AP_To_Wlan_Groups(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self.apply_wlangroup_to_active_ap()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'active_ap': '',
                     'wlan_group_name': '',
                     'radio_mode': 'bg',
                     'zd_tag': '',
                    }
        self.conf.update(conf)
        zd_tag = self.conf['zd_tag']
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']

        self.active_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['active_ap'])

        self.errmsg = ''
        self.passmsg = ''

    def apply_wlangroup_to_active_ap(self):
        try:
            #@author: anzuo, @since: 20140716, @change: can config multi-radio by parameter
            tmp_radio_list = []
            if type(self.conf['radio_mode']) != list:
                tmp_radio_list.append(self.conf['radio_mode'])
            else:
                tmp_radio_list = self.conf['radio_mode']
            
            for radio_mode in tmp_radio_list:
                lib.zd.ap.assign_to_wlan_group(self.zd, self.active_ap_mac,
                                               radio_mode, self.conf['wlan_group_name'])
            logging.info("wait 30s for configuration to be effective")
            time.sleep(30)# wait for configuration to be effective
            passmsg = 'The WLAN group "%s" is apply to the %s[%s] successfully'
            self.passmsg = passmsg % (self.conf['wlan_group_name'], self.conf['active_ap'], self.active_ap_mac)
        except Exception, e:
            self.errmsg = '[Apply failed]: %s' % e.message
