# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to assign all AP to empty wlan group on ZD
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Assign_All_APs_To_Empty_Wlan_Group(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._assign_all_aps_to_empty_wlan_group()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        msg = 'Assign All APs to WlanGroup [%s] on ZD Successfully' % self.wgs_cfg['name']
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = conf.copy()
        self.wgs_cfg = self.carrierbag['empty_wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        
    def _assign_all_aps_to_empty_wlan_group(self):
        self.errmsg = zhlp.ap.assign_all_ap_to_specific_wlan_group( self.zd,
                                                              self.wgs_cfg['name'])
