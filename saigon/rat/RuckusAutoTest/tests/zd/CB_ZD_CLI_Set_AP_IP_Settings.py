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
        - 'ap_mac_list': 'AP mac address list',
        - 'ip_cfg': 'AP IP configuration.'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set AP device IP setting as specified via CLI
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If set device IP setting successfully 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zdcli import configure_ap as config_ap

class CB_ZD_CLI_Set_AP_IP_Settings(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'ap_mac_list': 'AP mac address list',
                              'ip_cfg': 'AP IP configuration.'}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Set AP Device IP Settings via CLI")
            res, failed_aps = config_ap.configure_aps(self.zdcli, self.set_ap_cfg_list)
            
            if res == False:
                self.errmsg = "Configure APs IP setting failed for [%s]" % failed_aps
            #@author: yu.yanan #@since: 2014-6-10 add new parameter 'connect_flag'
            if self.conf.get('connect_flag'): 
                self._wait_for_aps_rejoin()
            else:
                pass
            
        except Exception, ex:
            self.errmsg = 'Can not set AP device IP settings via CLI successfully:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            self._update_carrier_bag()
            pass_msg = 'Set AP device IP settings successfully via CLI.'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        '''
        ip_version: ipv4, ipv6, dualstack.
        ipv4:
           ip_mode: ipv4 setting mode: manual/dhcp.
           ip_addr: ipv4 address.
           netmask: ipv4 net mask.
           gateway: ipv4 gateway.
           pri_dns: ipv4 primary dns.
           sec_dns: ipv4 secondary dns.
        ipv6:
           ipv6_mode: ipv6 setting mode: manual/auto.
           ipv6_addr: ipv6 address.
           ipv6_prefix_len: ipv6 prefix len.
           ipv6_gateway: ipv6 gateway.
           ipv6_pri_dns: ipv6 primary dns.
           ipv6_sec_dns: ipv6 secondary dns.
        '''
        #@author: yu.yanan #@since: 2014-6-10 add new parameter 'connect_flag'
        self.conf = {'ap_mac_list': [],
                     'ip_cfg': {},
                     'connect_flag':True}
        
        self.conf.update(conf)
        
        #Convert to ap configuration.
        default_ap_ip_cfg = {'ip_version': const.DUAL_STACK,
                             const.IPV4: {'ip_mode': 'dhcp',},
                             const.IPV6: {'ipv6_mode': 'auto'},
                             }
        
        ip_key_mapping = {'netmask':'net_mask',}
        
        if not self.conf['ip_cfg']:
            set_ap_ip_cfg = default_ap_ip_cfg
        else:
            set_ap_ip_cfg = self.conf['ip_cfg']
            
        new_set_ap_ip_cfg = {}
        for key, value in set_ap_ip_cfg.items():
            if key != 'ip_version':
                new_set_ap_ip_cfg.update(value)
            else:
                if ip_key_mapping.has_key(key):
                    new_set_ap_ip_cfg[ip_key_mapping[key]] = value
                else:
                    new_set_ap_ip_cfg[key] = value
                    
        if type(self.conf['ap_mac_list']) != list:
            ap_mac_list = [self.conf['ap_mac_list']]
        else:
            ap_mac_list = self.conf['ap_mac_list']                    
        
        self.ap_mac_list = ap_mac_list
        self.set_ap_cfg_list = []
        for ap_mac_addr in ap_mac_list:
            set_ap_cfg = {}
            set_ap_cfg['mac_addr'] = ap_mac_addr        
            set_ap_cfg['network_setting'] = new_set_ap_ip_cfg
            
            self.set_ap_cfg_list.append(set_ap_cfg)
            
        self.errmsg = ''
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.zd = self.testbed.components['ZoneDirector']
        
    def _wait_for_aps_rejoin(self):
        '''
        Wait for all ap rejoin after change ap ip mode.
        '''
        logging.info('Wait for APs are connected [%s]' % self.ap_mac_list)
        
        timeout = 480        
        res_aps_connected = []
        for mac_addr in self.ap_mac_list:
            res_ap_connected = self._wait_ap_connected(mac_addr, timeout)
            if res_ap_connected:
                res_aps_connected.append(res_ap_connected)
        
        if res_aps_connected:
            errmsg = "APs are not connected: %s" % res_aps_connected
            raise Exception(errmsg)
        
    def _wait_ap_connected(self, ap_mac_addr, timeout):
        '''
        Wait ap provisioning, till status is connected.
        '''
        end_time = time.time() + timeout
        err_d = {}
        while True:
            ap_info = self.zd.get_all_ap_info(ap_mac_addr)
            if ap_info:
                if ap_info['status'].lower().startswith("connected"):
                    logging.info("The provision process for the AP %s is completed successfully" % ap_mac_addr)
                    break
            if time.time() > end_time:
                if ap_info:
                    err_msg = "FAIL", "The AP %s is in the %s status instead of \"Connected\" status after %d seconds" % \
                                 (ap_mac_addr, ap_info['status'], timeout)
                    err_d[ap_mac_addr] = err_msg
                else:
                    err_msg = "FAIL", "The AP %s still does not appear in the AP-Summary table after %d seconds" % \
                                     (ap_mac_addr, timeout)
                    err_d[ap_mac_addr] = err_msg
                    
        return err_d 