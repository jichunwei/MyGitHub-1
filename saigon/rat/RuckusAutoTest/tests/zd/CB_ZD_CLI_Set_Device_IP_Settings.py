# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirectorCLI'
   Test parameters:
        - ip_cfg: ZD ip configuration.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set ZD device IP setting as specified via CLI
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
from RuckusAutoTest.components.lib.zdcli import sys_if_info as sysif

class CB_ZD_CLI_Set_Device_IP_Settings(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'ip_cfg': 'ZD IP configuration.'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        if self.conf.get('carribag_tag'):
            self._retrive_carrier_bag()
    def test(self):
        try:
            logging.info("Set ZD Device IP Settings via CLI")
            ip_type = const.IPV6 
            if self.conf.get('carribag_tag'):   #@yuyanan 2014-7-15 add get_zd_ip from carribag    
                sysif.set_sys_if(self.zdcli, self.carribag_set_zd_ip_cfg, ip_type)
            else:
                sysif.set_sys_if(self.zdcli, self.set_zd_ip_cfg, ip_type)
                
            logging.info("Get current ZD device IP settings via CLI")
            self.get_zd_ip_cfg = sysif.get_sys_if_info(self.zdcli)
            
            logging.info("Verify ZD device IP settings between CLI set and CLI get")
            if self.conf.get('carribag_tag'):
                self.errmsg = sysif.verify_device_ip_settings(self.carribag_set_zd_ip_cfg, self.get_zd_ip_cfg)
            else:
                self.errmsg = sysif.verify_device_ip_settings(self.set_zd_ip_cfg, self.get_zd_ip_cfg)
        except Exception, ex:
            self.errmsg = 'Can not set ZD device IP settings via CLI successfully:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Set ZD device IP settings successfully via CLI'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    def _retrive_carrier_bag(self):
        self.carribag_set_zd_ip_cfg = self.carrierbag['zdcli_sys_ip_info']
         
    def _update_carrier_bag(self):
        self.carrierbag['cli_zd_ip_cfg'] = self.get_zd_ip_cfg
        
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
        self.conf = {'carribag_tag':False}
       
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
                          #'vlan': '',
                          }
        
        self.conf.update(conf)
        
        if not self.conf.get('ip_cfg'):
            self.set_zd_ip_cfg = default_ip_cfg
        else:
            self.set_zd_ip_cfg = self.conf.get('ip_cfg')
            
            
        self.errmsg = ''
        self.zdcli = self.testbed.components['ZoneDirectorCLI']