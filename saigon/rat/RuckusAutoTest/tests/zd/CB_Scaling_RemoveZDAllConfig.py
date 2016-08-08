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

class CB_Scaling_RemoveZDAllConfig(Test):

    def config(self, conf):
        self.active_zd = None     
        self._retrieve_carribag()   
        self._cfgInitTestParams(conf)

    def test(self):
        logging.info('current zd is %s' % self.zd.ip_addr)
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
        if self.active_zd:
            self.zd = self.active_zd
        else:
            self.zd = self.testbed.components['ZoneDirector']
    
    
    
    def _retrieve_carribag(self):
        if 'active_zd' in self.carrierbag:
            self.active_zd = self.carrierbag['active_zd']
    

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        logging.info("Remove all Wlan Groups on the Zone Director.")
        lib.zd.wgs.remove_wlan_groups(self.zd, [])
#        delete by West.li,there is delete all wlan in remove_all_cfg
#        logging.info("Remove all WLAN on the Zone Director.")
#        lib.zd.wlan.delete_all_wlans(self.zd)
        self.zd.remove_all_cfg()

