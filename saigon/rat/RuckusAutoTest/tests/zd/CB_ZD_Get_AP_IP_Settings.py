# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Jan 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
        - 'ap_mac_list': 'AP mac address list',        
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get Current AP device IP setting via GUI
            
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If get ap ip settings successfully
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zd import access_points_zd

class CB_ZD_Get_AP_IP_Settings(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'ap_mac_list': 'AP mac address list',} 
    
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        try:
            self.passmsg = 'Get APs[%s] IP Settings in ZD WebUI successfully' % self.ap_mac_list
            logging.info('Get AP IP settings for %s' % self.ap_mac_list)
            ap_ip_cfg_dict = {}
            
            for ap_mac_addr in self.ap_mac_list:
                ip_type = const.IPV6            
                get_ap_ip_cfg = access_points_zd.get_ap_ip_config_by_mac(self.zd, ap_mac_addr, ip_type = ip_type)
                if get_ap_ip_cfg:                
                    ap_ip_cfg_dict[ap_mac_addr] = get_ap_ip_cfg
            
            self.ap_ip_cfg_dict = ap_ip_cfg_dict
                        
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_mac_list': []}
        
        self.conf.update(conf)
        
        if not self.conf['ap_mac_list']:
            self.ap_mac_list = self.testbed.config['ap_mac_list']
        else:
            if type(self.conf['ap_mac_list']) != list:
                self.ap_mac_list = [self.conf['ap_mac_list']]
            else:
                self.ap_mac_list = self.conf['ap_mac_list']
                
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        self.carrierbag['gui_ap_ip_cfg'] = self.ap_ip_cfg_dict