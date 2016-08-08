# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
        - ip_cfg: ZD ip configuration.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set ZD device IP setting as specified
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If set device IP setting successfully 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.common.utils import compare_dict
from RuckusAutoTest.components.lib.zd import system_zd as sys

class CB_ZD_Set_Device_IP_Settings(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'ip_cfg': 'ZD IP configuration.'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            ip_type = const.IPV6
            
            logging.info("Set ZD Device IP Settings via GUI")                    
            sys.set_device_ip_settings(self.zd, self.set_zd_ip_cfg, ip_type, self.l3switch)
            
            logging.info("Get current ZD device IP settings via GUI")
            self.get_zd_ip_cfg = sys.get_device_ip_settings(self.zd, ip_type)
            
            logging.info("Verify ZD device IP settings between GUI set and GUI get")
            self.errmsg = self._compare_set_get_ip_cfg(self.set_zd_ip_cfg, self.get_zd_ip_cfg)
            
        except Exception, ex:
            self.errmsg = 'Can not set ZD device IP settings successfully:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Set ZD device IP settings successfully.'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['gui_zd_ip_cfg'] = self.get_zd_ip_cfg 
        
    def _cfg_init_test_params(self, conf):
        '''
        ip_version: ipv4, ipv6, dualstack.
        vlan: ipv4 vlan.
        ipv4:
           ip_alloc: ipv4 setting mode: manual/dhcp.
           ip_addr: ipv4 address.
           netmask: ipv4 net mask.
           gateway: ipv4 gateway.
           pri_dns: ipv4 primary dns.
           sec_dns: ipv4 secondary dns.
        ipv6:
           ipv6_alloc: ipv6 setting mode: manual/auto.
           ipv6_addr: ipv6 address.
           ipv6_prefix_len: ipv6 prefix len.
           ipv6_gateway: ipv6 gateway.
           ipv6_pri_dns: ipv6 primary dns.
           ipv6_sec_dns: ipv6 secondary dns.
        '''
        self.conf = {}

        default_ip_cfg = {'ip_version': const.DUAL_STACK,
                          const.IPV4: {'ip_alloc': 'manual',
                                       'ip_addr': '192.168.0.2',
                                       'netmask': '255.255.255.0',
                                       'gateway': '192.168.0.253',
                                       'pri_dns': '192.168.0.252',
                                       'sec_dns': '',},
                          const.IPV6: {'ipv6_alloc': 'manual',
                                       'ipv6_addr': '2020:db8:1::2',
                                       'ipv6_prefix_len': '64',
                                       'ipv6_gateway': '2020:db8:1::251',
                                       'ipv6_pri_dns': '',
                                       'ipv6_sec_dns': ''},
                          #'vlan': '1',
                          }
        
        self.conf.update(conf)
        
        if not self.conf['ip_cfg']:
            self.set_zd_ip_cfg = default_ip_cfg
        else:
            self.set_zd_ip_cfg = self.conf['ip_cfg']
            
        self.errmsg = ''
        if self.conf.has_key("zd"):
            self.zd = self.carrierbag.get(self.conf.get("zd"))
        else:
            self.zd = self.testbed.components['ZoneDirector']
        self.l3switch = self.testbed.components['L3Switch']
        
        
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
                    
                    key_ip_alloc = 'ip_alloc'
                    set_ipv4_alloc = set_ipv4_cfg.get(key_ip_alloc)
                    get_ipv4_alloc = get_ipv4_cfg.get(key_ip_alloc)
                    
                    if set_ipv4_alloc and get_ipv4_alloc and set_ipv4_alloc.lower() == get_ipv4_alloc.lower():
                        if set_ipv4_alloc.lower() in ['manual','static']:
                            err_msg = compare_dict(set_ipv4_cfg, get_ipv4_cfg, op = 'eq')
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
                    
                    key_ipv6_alloc = 'ipv6_alloc'
                    set_ipv6_alloc = set_ipv6_cfg.get(key_ipv6_alloc)
                    get_ipv6_alloc = get_ipv6_cfg.get(key_ipv6_alloc)
                    
                    if set_ipv6_alloc and get_ipv6_alloc and set_ipv6_alloc.lower() == get_ipv6_alloc.lower():
                        if set_ipv6_alloc == 'manual':
                            err_msg = compare_dict(set_ipv6_cfg, get_ipv6_cfg, op = 'eq')
                    else:
                        err_msg = 'Error: Item ipv6 alloc has difference (%s,%s)' % (set_ipv6_alloc, get_ipv6_alloc)
                    
                else:
                    if not set_ip_cfg.has_key(key_ipv6):
                        err_msg = 'No ipv6 configuration in set config: %s' % set_ip_cfg
                    else:
                        err_msg = 'No ipv6 configuration in get config: %s' % get_ip_cfg
                
                if err_msg:
                    res_err[key_ipv6] = err_msg
            
            key_vlan = 'vlan'
            if set_ip_cfg.has_key(key_vlan):
                if set_ip_cfg.get(key_vlan) != get_ip_cfg.get(key_vlan):
                    err_msg = 'Item vlan has difference (%s,%s)' % (set_ip_cfg.get(key_vlan), get_ip_cfg.get(key_vlan))
                
        else:
            if set_ip_version == get_ip_version:
                err_msg = 'IP version is null in both set and get.'                    
            else:
                err_msg = 'Error: Item ip version has difference (%s,%s)' % (set_ip_version, get_ip_version)
            res_err['ip_version'] = err_msg
                    
        return res_err