# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Aprial 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'L3Switch'
   Test parameters:
       N/A
        
   Test procedure:
    1. Config:
        - initialize test parameters
        - Get switch from testbed.components
        - Get interface from carrier bag                
    2. Test:
        - Enable interface on Switch
        - Disable interface on Switch
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: The interface of specified ZD are enabled. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging
from RuckusAutoTest.models import Test


class CB_ZD_Recreate_All_APs(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        self._create_ap_components()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            passmsg = 'Re-create APs [%s] successfully' % (self.ap_mac_list)
            return self.returnResult('PASS', passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf = {'zd_tag': '',
                     'ap_mac_list': ''}
        
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
        
        zd_tag = self.conf['zd_tag']
        
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
    def _update_carrier_bag(self):
        pass

    def _create_ap_components(self):
        '''
        Recreate all ap components based on AP ip changes.
        '''
        try:
            all_aps_info = self.zd.get_all_ap_info()
            
            if self.conf['ap_mac_list']:
                self.ap_mac_list = self.conf['ap_mac_list']
            else:
                self.ap_mac_list = self.testbed.config['ap_mac_list']
            
            '''
            ap_components = []
            
            ap_conf = {'username': self.zd.username,
                       'password': self.zd.password}
            '''
            
            for ap_info in all_aps_info:
                for ap_mac in self.ap_mac_list:
                    if ap_info['mac'].lower() == ap_mac.lower():
                        ap_obj = self.testbed.mac_to_ap[ap_mac.lower()]
                        ap_obj.ip_addr = ap_info['ip_addr']
                        logging.debug("AP IP:%s, Version %s" % (ap_obj.ip_addr, ap_obj.get_version()))
        except Exception, ex:
            self.errmsg = "Error:%s" % ex.message
