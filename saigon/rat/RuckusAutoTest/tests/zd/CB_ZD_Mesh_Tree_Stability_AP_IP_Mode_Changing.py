# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if the mesh tree are match with expected 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If the mesh tree is not changed
            FAIL: If the mesh tree is changed

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_Mesh_Tree_Stability_AP_IP_Mode_Changing(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        self._change_active_ap_ip_mode()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_aps_info()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_ap_ip_info()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'time_out': 1200}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        self.test_mode = ['ipv6', 'dual']
        
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        if self.carrierbag.get('expected_aps_info'):
            self.expected_aps_info = self.carrierbag['expected_aps_info']
        else:
            self.expected_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
    
    def _verify_aps_info(self):
        logging.debug('The expected APs info:\n %s' % pformat(self.expected_aps_info))
        
        lost_aps = []
        error_aps = []
        start_time = time.time()
        
        while True:
            if time.time() - start_time > self.conf['time_out']:
                break
            current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
            #logging.debug('The current APs info: \n %s' % pformat(current_aps_info))
            
            lost_aps = []
            error_aps = []
            for mac_addr in self.expected_aps_info.keys():
                if mac_addr not in current_aps_info.keys():
                    lost_aps.append(mac_addr)
                    continue
                if current_aps_info[mac_addr]['status'] != self.expected_aps_info[mac_addr]['status']:
                    error_aps.append(mac_addr)
                    continue
            logging.debug('lost aps: %s' % lost_aps)
            logging.debug('error aps: %s' % error_aps)
            if not lost_aps and not error_aps:
                self.passmsg += '; all APs are reconnected as effected.'
                return
            
            time.sleep(60)
            
        if lost_aps:
            self.errmsg = 'There are APs %s lost.' % lost_aps 
        if error_aps:
            self.errmsg += 'The APs %s have the information is not match with expected' % error_aps 
    
    def _change_active_ap_ip_mode(self):
        ap_ip_settings = lib.apcli.sysgrp.get_ip_settings(self.active_ap, 'wan')
        logging.info('Current AP IP mode: %s' % ap_ip_settings['ip_mode'])
        if ap_ip_settings['ip_mode'] == 'ipv6':
            self.new_ip_mode = 'dual'
            new_ip_settings = {'ip_version': 'dualstack',
                               'ipv4': {'ip_mode': 'dhcp',},
                               'ipv6': {'ipv6_mode': 'auto',},
         }
        elif ap_ip_settings['ip_mode'] == 'dual':
            self.new_ip_mode = 'ipv6'
            new_ip_settings = {'ip_version': 'ipv6',
                               'ipv6': {'ipv6_mode': 'auto',},
         }
        else:
            self.errmsg  = 'AP is under %s mode. We do not support the test for this mode.' % ap_ip_settings['ip_mode']
            return
            
        logging.info('Change the AP[%s] IP mode to %s' % (self.active_ap.base_mac_addr, new_ip_settings))
        lib.zd.ap.set_ap_ip_config_by_mac_addr(self.zd, self.active_ap.base_mac_addr, '', new_ip_settings, 'ipv6')
        self.passmsg = 'The AP IP mode is changed successfully' 
        time.sleep(30) # The AP will be reboot after the IP mode changed
    
    def _verify_ap_ip_info(self):
        current_ap_ip_settings = lib.apcli.sysgrp.get_ip_settings(self.active_ap, 'wan')
        if current_ap_ip_settings['ip_mode'] != self.new_ip_mode:
            self.errmsg = 'The IP mode of AP[%s] is "%s" but "%s" as expected.' % (self.active_ap.base_mac_addr,
                                                                                   current_ap_ip_settings['ip_mode'],
                                                                                   self.new_ip_mode)
            return
        
        self.passmsg += '; the IP mode of AP[%s] is "%s" as expected.' % (self.active_ap.base_mac_addr,
                                                                         current_ap_ip_settings['ip_mode'])
        
