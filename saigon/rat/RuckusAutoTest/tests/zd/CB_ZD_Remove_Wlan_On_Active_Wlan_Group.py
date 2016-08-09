import os
import re
import time
import logging
import libZD_TestConfig as tconfig
import libZD_TestMethods as tmethod
import libZD_TestMethods_v8 as tmethod8

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.common import Ratutils as utils
from pprint import pprint, pformat

class CB_ZD_Remove_Wlan_On_Active_Wlan_Group(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._removeActiveWlansFromWlanGroup()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self.carrierbag['active_phone'] = {}
        msg = "Remove wlans from wlan group [%s] successfully" %\
              (self.carrierbag['wgs_cfg']['name'])
              
        return self.returnResult("PASS", msg)
        
    def cleanup(self):
        pass
        #self._removeActiveWlansFromWlanGroup()
        #self.carrierbag['active_phone']={}
        
    def _cfgInitTestParams(self, conf):
        self.conf = dict( ping_timeout=60,
                          check_status_timeout=240,
                          check_wlan_timeout=30,
                          check_dhcp_timeout=30,
                          break_time=3,
                          radio_mode='')
        self.conf.update(conf)
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        self.wgs_cfg = self.carrierbag['wgs_cfg'].copy()

    def _removeActiveWlansFromWlanGroup(self):
        self.wlan_list = zhlp.wlan.get_wlan_list(self.zd)
        logging.info("Remove wlans on wlan group")
        try:
            zhlp.wgs.cfg_wlan_group_members(self.zd, self.wgs_cfg['name'], self.wlan_list, False)
            tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
        except Exception, e:
            self.errmsg = e.message

