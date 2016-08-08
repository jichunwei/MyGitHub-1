"""
Description: This script is support to remove wlan on wlan group
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import logging
import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Remove_Wlan_On_Wlan_Group(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._removeActiveWlansFromWlanGroup()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self.carrierbag['active_phone'] = {}
        msg = "Remove wlan %s from wlan group [%s] successfully" %\
              (self.wlan_list, self.wgs_cfg['name'])
              
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
        self.wgs_cfg = self.conf['wgs_cfg'] if self.conf.has_key('wgs_cfg') else self.carrierbag['wgs_cfg']
        self.wlan_list = self.conf['wlan_list']

    def _removeActiveWlansFromWlanGroup(self):        
        logging.info("Remove wlans[%s] on wlan group[%s]" % (str(self.wlan_list), self.wgs_cfg['name']))
        try:
            zhlp.wgs.cfg_wlan_group_members(self.zd, self.wgs_cfg['name'], self.wlan_list, False)
            tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
        except Exception, e:
            self.errmsg = e.message

