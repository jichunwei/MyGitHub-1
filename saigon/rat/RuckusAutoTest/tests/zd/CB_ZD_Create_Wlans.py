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

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Create_Wlans(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyCreateWlans()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        self._verifyTheWlanListOnWebUI()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = passmsg + ', %s' % self.passmsg

        self._verifyTheAPsConnectedStatus()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = passmsg + ', %s' % self.passmsg

        self._updateCarrierBag()

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'wlan_cfg_list': [],
                     'wlan_cfg_set': '',
                     'pause': 1
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']

        if not self.conf.get('wlan_cfg_list'):
            self.conf['wlan_cfg_list'] = tconfig.get_wlan_profile(self.conf['wlan_cfg_set'])

        if self.carrierbag.get('existing_aps_connection_status'):
            self.existing_aps_connection_status = self.carrierbag['existing_aps_connection_status']

        else:
            all_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
            self.existing_aps_connection_status = {}
            for ap in all_aps_info.keys():
                self.existing_aps_connection_status[ap] = all_aps_info[ap]['status']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyCreateWlans(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            current_wlanlist = lib.zd.wlan.get_wlan_list(self.zd)
            if current_wlanlist == None: current_wlanlist = []
            for wlan_cfg in self.conf['wlan_cfg_list']:
                if wlan_cfg['ssid'] in current_wlanlist:
                    self._cfgEditWlanOnZD(wlan_cfg)
                else:
                    self._cfgCreateWlanOnZD(wlan_cfg)
#                if self.errmsg: return self.returnResult("FAIL", self.errmsg)
#            lib.zd.wlan.create_multi_wlans(self.zd, self.conf['wlan_cfg_list'], self.conf['pause'])
            self.expected_wlan_name_list = [wlan['ssid'] for wlan in self.conf['wlan_cfg_list']]
            self.passmsg = 'The WLANs %s are created successfully' % self.expected_wlan_name_list
            logging.debug(self.passmsg)

        except Exception, e:
            self.errmsg = '[WLANs creating failed] %s' % e.message
            logging.debug(self.errmsg)
    
    def _cfgEditWlanOnZD(self, wlan_cfg):
        logging.info("Edit WLAN [%s] with new setting on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, wlan_cfg['ssid'], wlan_cfg)
#        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _cfgCreateWlanOnZD(self, wlan_cfg):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, wlan_cfg)
#        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")
    

    def _verifyTheWlanListOnWebUI(self):
        # Verify the WLANs list show on the ZD if they are match with the expected WLANs
        self.wlan_list_on_zd = lib.zd.wlan.get_wlan_list(self.zd)
        for wlan in self.expected_wlan_name_list:
            if wlan not in self.wlan_list_on_zd:
                msg = 'The WLAN[%s] are not shown on Zone Director'
                self.errmsg = msg % wlan
                logging.debug(self.errmsg)
                return

        self.passmsg = 'WLANs %s are shown on Zone Director correctly' % self.expected_wlan_name_list
        logging.debug(self.passmsg)

    def _verifyTheAPsConnectedStatus(self):
        # Verify if the APs connection status be changed or not
        all_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        all_aps_connection_status = {}
        for ap in all_aps_info.keys():
            all_aps_connection_status[ap] = all_aps_info[ap]['status']
        if all_aps_connection_status != self.existing_aps_connection_status:
            errmsg = 'The connection status of APs changed to %s instead of %s'
            self.errmsg = errmsg % (all_aps_connection_status, self.existing_aps_connection_status)
            return

        self.passmsg = '[The APs connection status is correctly][%s]' % all_aps_connection_status
        logging.debug(self.errmsg)

    def _updateCarrierBag(self):
        self.carrierbag['existing_wlans_list'] = self.wlan_list_on_zd
