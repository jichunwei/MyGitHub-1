# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to remove all config on ZD
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import os
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_RemoveZDAllConfig(Test):

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
        self.zd = self.testbed.components['ZoneDirector']

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        logging.info("Remove all Wlan Groups on the Zone Director.")
        lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        logging.info("Remove all WLAN on the Zone Director.")
        lib.zd.wlan.delete_all_wlans(self.zd)
        self.zd.remove_all_cfg()

