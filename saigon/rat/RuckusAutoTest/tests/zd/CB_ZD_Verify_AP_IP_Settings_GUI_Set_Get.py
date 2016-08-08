# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - set_ip_cfg: ZD ip configuration has been set.
        - ap_mac_addr: AP mac address
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Compare the data between GUI get and set          
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If data are same between get and set 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common.utils import compare_dict_key_value

class CB_ZD_Verify_AP_IP_Settings_GUI_Set_Get(Test):
    required_components = []
    parameters_description = {'set_ip_cfg': 'ZD IP configuration.',
                              'ap_mac_addr': 'AP mac address',
                              }
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Verify GUI set and get values for AP device IP settings")
            
            err_dict = {}
            
            for ap_mac_addr in self.ap_mac_list:
                errmsg = ''
                if self.gui_get_ap_ip_cfg.has_key(ap_mac_addr):
                    gui_get_ap_cfg = self.gui_get_ap_ip_cfg[ap_mac_addr]
                    errmsg = self._compare_set_get_ip_cfg(self.set_ap_ip_cfg, gui_get_ap_cfg)
                else:
                    errmsg = "No AP IP setting of GUI get"
                
                if errmsg:
                    err_dict[ap_mac_addr] = errmsg
                    
            if err_dict:
                self.errmsg = 'Data of AP IP setting are different between GUI set and get: %s' % err_dict

        except Exception, ex:
            self.errmsg = 'GUI set and get failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            pass_msg = 'GUI get and set data are same'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {'set_ip_cfg': {},
                     'ap_mac_list': ''}
        self.conf.update(conf)
        
        self.gui_set_ap_ip_cfg = self.conf['set_ip_cfg']
        
        if type(self.conf['ap_mac_list']) != list:
            self.ap_mac_list = [self.conf['ap_mac_list']]
        else:
            self.ap_mac_list = self.conf['ap_mac_list']
            
        self.set_ap_ip_cfg = self.conf['set_ip_cfg']
        self.gui_get_ap_ip_cfg = self.carrierbag['gui_ap_ip_cfg']
             
        self.errmsg = ''
        
    def _compare_set_get_ip_cfg(self, set_ip_cfg, get_ip_cfg):
        '''
        Compare get and set IP configuration.        
        '''
        res_err = {}
        logging.info('Set config: %s, Get config: %s' % (set_ip_cfg, get_ip_cfg))
        
        key_version = 'ip_version'
        set_ip_version = set_ip_cfg.get(key_version)
        get_ip_version = get_ip_cfg.get(key_version)
        
        if set_ip_version and get_ip_version and set_ip_version.lower() == get_ip_version.lower():
            if get_ip_version in [const.IPV4, const.DUAL_STACK]:
                err_msg = ''
                key_ipv4 = const.IPV4
                if set_ip_cfg.has_key(key_ipv4) and get_ip_cfg.has_key(key_ipv4):
                    set_ipv4_cfg = set_ip_cfg[key_ipv4]
                    get_ipv4_cfg = get_ip_cfg[key_ipv4]
                    
                    key_ip_alloc = 'ip_mode'
                    set_ipv4_alloc = set_ipv4_cfg.get(key_ip_alloc)
                    get_ipv4_alloc = get_ipv4_cfg.get(key_ip_alloc)
                    
                    if set_ipv4_alloc and get_ipv4_alloc and set_ipv4_alloc.lower() == get_ipv4_alloc.lower():
                        if set_ipv4_alloc.lower() in ['manual','static']:
                            err_msg = compare_dict_key_value(set_ipv4_cfg, get_ipv4_cfg)
                    else:
                        err_msg = 'Error: Item ipv4 alloc has difference (%s,%s)' % (set_ipv4_alloc, get_ipv4_alloc)
                    
                else:
                    if not set_ip_cfg.has_key(key_ipv4):
                        err_msg = 'No ipv4 configuration in set config: %s' % set_ip_cfg
                    else:
                        err_msg = 'No ipv4 configuration in get config: %s' % get_ip_cfg
                        
                if err_msg:
                    res_err[key_ipv4] = err_msg
                
            if get_ip_version in [const.IPV6, const.DUAL_STACK]:
                err_msg = ''
                
                key_ipv6 = const.IPV6
                if set_ip_cfg.has_key(key_ipv6) and get_ip_cfg.has_key(key_ipv6):
                    set_ipv6_cfg = set_ip_cfg[key_ipv6]
                    get_ipv6_cfg = get_ip_cfg[key_ipv6]
                    
                    key_ipv6_alloc = 'ipv6_mode'
                    set_ipv6_alloc = set_ipv6_cfg.get(key_ipv6_alloc)
                    get_ipv6_alloc = get_ipv6_cfg.get(key_ipv6_alloc)
                    
                    if set_ipv6_alloc and get_ipv6_alloc and set_ipv6_alloc.lower() == get_ipv6_alloc.lower():
                        if set_ipv6_alloc == 'manual':
                            err_msg = compare_dict_key_value(set_ipv6_cfg, get_ipv6_cfg)
                    else:
                        err_msg = 'Error: Item ipv6 alloc has difference (%s,%s)' % (set_ipv6_alloc, get_ipv6_alloc)
                    
                else:
                    if not set_ip_cfg.has_key(key_ipv6):
                        err_msg = 'No ipv6 configuration in set config: %s' % set_ip_cfg
                    else:
                        err_msg = 'No ipv6 configuration in get config: %s' % get_ip_cfg
                
                if err_msg:
                    res_err[key_ipv6] = err_msg
                
        else:
            if set_ip_version == get_ip_version:
                err_msg = 'IP version is null in both set and get.'                    
            else:
                err_msg = 'Error: Item ip version has difference (%s,%s)' % (set_ip_version, get_ip_version)
            res_err['ip_version'] = err_msg
                    
        return res_err