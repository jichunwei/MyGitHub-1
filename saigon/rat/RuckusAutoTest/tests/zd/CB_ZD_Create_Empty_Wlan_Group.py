# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to create a wlan group on ZD
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
#Update the script by Jacky Luh@2011-08-19
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_groups_zd as wgs

class CB_ZD_Create_Empty_Wlan_Group(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._create_wlan_group_without_wlan()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag['empty_wgs_cfg'] = self.conf
        msg = 'Create WlanGroup [%s] on ZD Successfully' % self.conf['name']
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = {'name': 'EmptyWlanGroup',
                     'description': 'EmptyWlanGroup',
                    }
        self.conf.update(conf)
       
        self.zd = self.testbed.components['ZoneDirector']
         
    def _create_wlan_group_without_wlan(self):
        self.errmsg = wgs.create_wlan_group(self.zd, 
                                            self.conf['name'],
                                            [],
                                            False,
                                            self.conf['description'])
        
        
