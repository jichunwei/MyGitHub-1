# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to remove all config on ZD
Author: chris
Email: cwang@ruckuswireless.com
"""
import os
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl

class CB_ZD_SR_RemoveZDAllConfig(Test):

    def config(self, conf):
        self._cfgInitTestParams(conf)

    def test(self):
        try:
            self._cfgRemoveZDWlanGroupsAndWlan()
        except Exception, ex:
            self.errmsg = ex.message
        if self.errmsg: return ("FAIL", self.errmsg)
        msg = 'Remove Configuration on ZD Successfully'
        return self.returnResult("PASS", msg)

    def cleanup(self):
        pass

    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.zd = self.carrierbag['active_zd']

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        logging.info("Remove all Wlan Groups on the Zone Director.")
        lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        logging.info("Remove all WLAN on the Zone Director.")
        lib.zd.wlan.delete_all_wlans(self.zd)
        self.zd.remove_all_cfg()
        mgmt_ip_acl.delete_all_mgmtipacl(self.zd)
        self.zd.delete_all_maps()
