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
        - 'ap_mac_list': 'AP mac address list',
        - 'ip_cfg': 'AP IP configuration.'
        - 'ap_tag': 'AP tag'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set AP device IP setting as specified
        - Get Current AP device IP setting via GUI
        - Compare the data between get and set    
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If set AP IP setting successfully and data are same between get and set 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zd import access_points_zd

class CB_ZD_Config_AP_IP_Settings(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'ap_mac_list': 'AP mac address list',
                              'ip_cfg': 'AP IP configuration.',
                              'ap_tag': 'AP tag'
                              } 
    
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        try:
            self.passmsg = 'Configure APs[%s] IP Settings in ZD WebUI successfully' % self.ap_mac_list
            
            err_msg_dict = {}
            pass_aps = []
            for ap_mac in self.ap_mac_list:
                ip_type = const.IPV6
                logging.info('Configure AP[%s] IP Settings in ZD WebUI' % ap_mac)
                err_msg = access_points_zd.set_ap_ip_config_by_mac_addr(self.zd, ap_mac, '', self.ap_ip_cfg, ip_type = ip_type)
            
                if err_msg:
                    err_msg_dict[ap_mac] = err_msg
                else:
                    pass_aps.append(ap_mac)
                    #@author: liang aihua,@since: 2015-2-10,@change: when change ap's ip, connection mode don;t need to configure.
                    #jluh added by 2013-10-11
                    #self.testbed.configure_ap_connection_mode(ap_mac, self.mode)
                                                                                     
            if pass_aps:
                self._wait_for_aps_rejoin(self.ap_mac_list)
            
            if err_msg_dict:
                self.errmsg = 'Fail to configure AP as %s, error: %s' % (self.ap_ip_cfg, err_msg_dict)
            
        except Exception, ex:
            self.errmsg = ex.message
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_mac_list': [],
                     'ip_cfg': '', 
                     'ap_tag': '',
                     'mode': ''
                     }
        
        default_ip_cfg = {'ip_version': const.DUAL_STACK,
                          const.IPV4: {'ip_mode': 'as_is'},
                          const.IPV6: {'ipv6_mode': 'as_is',},
                          }
        
        self.conf.update(conf)
        
        if not self.conf.get('ip_cfg'):
            self.conf['ip_cfg'] = default_ip_cfg
        
        self.ap_ip_cfg = self.conf['ip_cfg']
        self.mode = self.conf['mode']
        
        if self.conf['ap_tag']:
            if type(self.conf['ap_tag']) == list:
                ap_tag_list = self.conf['ap_tag']
            else:
                ap_tag_list = [self.conf['ap_tag']]
                
            ap_mac_list = []
            for ap_tag in ap_tag_list:
                ap_dict = self.carrierbag.get(ap_tag)
                if ap_dict:
                    active_ap = ap_dict['ap_ins']
                    ap_mac_addr = ap_dict['ap_mac']
                    ap_mac_list.append(ap_mac_addr)
                    
            self.ap_mac_list = ap_mac_list
        else:   
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
        
        
    def _wait_for_aps_rejoin(self, ap_mac_list):
        '''
        Wait for all ap rejoin after change ap ip mode.
        '''
        logging.info('Wait 480 seconds for APs are connected [%s]' % ap_mac_list)
        
        timeout = 480        
        res_aps_connected = []
        for mac_addr in ap_mac_list:
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
                    ap_obj = self.testbed.mac_to_ap[ap_mac_addr.lower()]
                    ap_obj.ip_addr = ap_info['ip_addr']
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