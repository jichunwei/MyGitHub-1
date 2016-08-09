"""
   Description: 
   This test class support to verify packet capture ip column title 
   @since: May 2014
   @author: Yuyanan

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - check the IP column title  according to the ap ip address and system ip       
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Verify packet capture ip column title success 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import admin_diagnostics as ad


class CB_ZD_Verify_Packet_Capture_Ip_Column_Title(Test):
        
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self._get_system_ip_mode()
        self._verify_ap_ip_column_title()
        self._verify_capture_ip_column_title()
        
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = 'The packet capture ip column title is the same as the system ip mode'
        
    def _retrive_carrier_bag(self):
        self.get_zd_ip_cfg = self.carrierbag['cli_zd_ip_cfg']
            
    def _get_system_ip_mode(self):
        self.zd_ip_mode_map={'IPv4-Only':'ip_address','dual stack':'ipv4_ipv6_address','IPv6-Only':'ipv6_address'}
        system_ip_mode = self.get_zd_ip_cfg.get('Protocol Mode')
        self.expect = self.zd_ip_mode_map.get(system_ip_mode)
 
    def _verify_ap_ip_column_title(self):
        table_title_list = ad.get_current_aps_table_title(self.zd)
        self._verify_process(table_title_list)
                    
    def _verify_capture_ip_column_title(self): 
        table_title_list = ad.get_capture_aps_table_title(self.zd)
        self._verify_process(table_title_list)
        
    def _verify_process(self,table_title_list):
        ip_title_flag = 0
        for actual in table_title_list:
            if self.expect == actual:
                ip_title_flag = 1
                return True
            
        ap_target_title_list = []
        for key,value in self.zd_ip_mode_map.items():
            ap_target_title_list.append(value)
        
        if ip_title_flag == 0:
            for actual in table_title_list:
                if actual in ap_target_title_list:
                    self.errmsg += " [expect]:%s -- [actual]:%s" % (self.expect,actual)
                    return False
            self.errmsg += " [expect]:%s -- [actual]:not found" % (self.expect)


