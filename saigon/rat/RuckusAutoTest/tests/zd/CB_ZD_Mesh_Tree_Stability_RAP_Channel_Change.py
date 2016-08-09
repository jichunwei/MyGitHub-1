# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Dec 2011

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
import re
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_Mesh_Tree_Stability_RAP_Channel_Change(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        self._change_root_ap_channel()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_aps_info()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_aps_channel()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'time_out': 180}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.root_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.verify_aps = [self.carrierbag[tag]['ap_ins'] for tag in self.conf['verify_aps']]
        if self.carrierbag.get('expected_aps_info'):
            self.expected_aps_info = self.carrierbag['expected_aps_info']
        else:
            self.expected_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
    
    def _verify_aps_info(self):
        logging.debug('The expected APs info:\n %s' % pformat(self.expected_aps_info))
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        logging.debug('The current APs info: \n %s' % pformat(current_aps_info))
               
        lost_aps = []
        error_aps = []
        for mac_addr in self.expected_aps_info.keys():
            if mac_addr not in current_aps_info.keys():
                lost_aps.append(mac_addr)
                continue
            if current_aps_info[mac_addr]['status'] != self.expected_aps_info[mac_addr]['status']:
                error_aps.append(mac_addr)
                continue
        
        if lost_aps:
            self.errmsg = 'There are APs %s lost.' % lost_aps 
        if error_aps:
            self.errmsg += 'The APs %s have the information is not match with expected' % error_aps 
        
        if self.errmsg:
            return
        
        self.passmsg += '; all APs are reconnected as effected.'
    
    def _change_root_ap_channel(self):
        logging.info('Change the Root AP channel: %s' % self.conf['radio_cfg'])
        lib.zd.ap.cfg_ap(self.zd, self.root_ap.base_mac_addr, self.conf['radio_cfg'])
        self.passmsg = 'The channel setting is changed successfully'
    
    def _verify_aps_channel(self):
        start_time = time.time()
        incorrect_info = []
        while True:
            if time.time() - start_time > self.conf['time_out']:
                break
            incorrect_info = []
            current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
            for ap in self.verify_aps:
                #@Jane.Guo @since: 2013-06-04 fix bug of dualband AP
                if not re.search(self.conf['radio_cfg']['channel'],current_aps_info[ap.base_mac_addr]['channel']):
                    incorrect_info.append((ap.base_mac_addr, 
                                           current_aps_info[ap.base_mac_addr]['channel']))
                    
            if not incorrect_info:
                self.passmsg += '; all related APs have same channel with Root AP [%s]' % current_aps_info[self.root_ap.base_mac_addr]['channel']
                return
            
            time.sleep(30)
        
        if incorrect_info:
            self.errmsg = 'There is different channel info at %s' % incorrect_info
