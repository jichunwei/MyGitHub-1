"""
   Description: 
   This test class support to verify the packet capture ip column value 
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
        - Get the Ip address from packet capture and check it.    
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Verify ip address from packet capture web as the same as ip address from monitor current ap ip web 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import admin_diagnostics as ad
from RuckusAutoTest.common.utils import list_to_dict
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as aphlp
from RuckusAutoTest.common import Ratutils  as ratuil 
import re


class CB_ZD_Verify_Packet_Capture_Ip_Column_Value(Test):
        
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.system_ip_mode = self.get_zd_ip_cfg.get('Protocol Mode')
        self._verify_ap_ip_column_value()
        self._verify_capture_ip_column_value()
            
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
            self.get_zd_ip_cfg = self.carrierbag['cli_zd_ip_cfg']

    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']   
        self.zdcli = self.testbed.components['ZoneDirectorCLI']     
        self.errmsg = ''
        self.passmsg = 'The Ip column value from packet capture check success'
        
    def _verify_ap_ip_column_value(self):
        cur_aps_dict = ad.get_current_aps_from_admin_diagnostics(self.zd)
        self._verify_process(cur_aps_dict)
            
    def _verify_capture_ip_column_value(self):
        capture_aps = ad.get_capture_aps(self.zd)
        self._verify_process(capture_aps)
        
    #@author:{ap_mode:ipv4-only, ap_ip:ipv4} {ap_mode:ipv6-only, ap_ip:ipv6} {ap_mode:dual, ap_ip:ipv4,ap_ipv6:ipv6} 
    def _verify_process(self,aps_dict):
        for key_mac in aps_dict:
            ap_ip = aps_dict.get(key_mac).get('ip_addr')
            ap_ipv6 = aps_dict.get(key_mac).get('ipv6')
             
            self.ap_cfg = aphlp.show_ap_info_by_mac(self.zdcli, key_mac)
            if self.ap_cfg:
                _cfg = self.ap_cfg['AP']['ID']
                self.ap_cfg = _cfg.values()[0]
                ap_mode = self.ap_cfg['Network Setting']['Protocol mode']
            if self.system_ip_mode == "IPv4-Only":
                if ap_mode == "IPv4-Only" or ap_mode == "IPv4 and IPv6":
                    if ratuil.is_ipv4_addr(ap_ip) and not ratuil.is_ipv6_addr(ap_ipv6):
                        pass
                    else:
                        self.errmsg += "[system ip mode]:%s---[ap_mode]:%s,[ap_ip]:%s---[ap_ipv6]:%s" %(self.system_ip_mode,ap_mode,ap_ip,ap_ipv6)
            elif self.system_ip_mode == "IPv6-Only":
                if ap_mode == "IPv6-Only" or ap_mode == "IPv4 and IPv6":
                    if ratuil.is_ipv6_addr(ap_ip) and not ratuil.is_ipv4_addr(ap_ipv6):
                        pass
                    else:
                        self.errmsg += "[system ip mode]:%s---[ap_mode]:%s,[ap_ip]:%s---[ap_ipv6]:%s" %(self.system_ip_mode,ap_mode,ap_ip,ap_ipv6)
            elif self.system_ip_mode == "dual stack":
                if ap_mode == "IPv4-Only":
                    if ratuil.is_ipv4_addr(ap_ip) and not ratuil.is_ipv6_addr(ap_ipv6):
                        pass
                    else:
                        self.errmsg += "[system ip mode]:%s---[ap_mode]:%s,[ap_ip]:%s---[ap_ipv6]:%s" %(self.system_ip_mode,ap_mode,ap_ip,ap_ipv6)
                elif ap_mode == "IPv6-Only":
                    if ratuil.is_ipv6_addr(ap_ipv6) and not ratuil.is_ipv4_addr(ap_ip):
                        pass
                    else:
                        self.errmsg += "[system ip mode]:%s---[ap_mode]:%s,[ap_ip]:%s---[ap_ipv6]:%s" %(self.system_ip_mode,ap_mode,ap_ip,ap_ipv6)
                elif ap_mode == "IPv4 and IPv6":
                    if ratuil.is_ipv4_addr(ap_ip) and ratuil.is_ipv6_addr(ap_ipv6):
                        pass
                    else:
                        self.errmsg += "[system ip mode]:%s---[ap_mode]:%s,[ap_ip]:%s---[ap_ipv6]:%s" %(self.system_ip_mode,ap_mode,ap_ip,ap_ipv6)
            else:
                self.errmsg += "[system ip mode]:%s---" %(self.system_ip_mode)
