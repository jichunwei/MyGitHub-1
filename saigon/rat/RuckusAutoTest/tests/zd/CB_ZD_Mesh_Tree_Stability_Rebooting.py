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
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_Mesh_Tree_Stability_Rebooting(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        test_funcs = {'reboot_ap': self._test_reboot_ap,
                      'reboot_zd': self._test_reboot_zd}
        
        test_funcs[self.conf['test_option']]()
        
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {'time_out': 1500}
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.get('ap_tag'):
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        else:
            self.active_ap = None
            
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
                
            if not lost_aps and not error_aps:
                self.passmsg += '; all APs are reconnected as effected.'
                return
            
            time.sleep(60)
            
        if lost_aps:
            self.errmsg = 'There are APs %s lost.' % lost_aps 
        if error_aps:
            self.errmsg += 'The APs %s have the information is not match with expected' % error_aps 
        
    def _test_reboot_ap(self):
        ap_ipaddr = self.active_ap.ip_addr
        ap_mac = self.active_ap.base_mac_addr
        logging.info("Reboot AP[%s] and verify Mesh Tree will not change after AP reboot" % ap_ipaddr)
        lib.zd.mma.restart_ap_by_mac(self.zd, ap_mac)

        logging.info("Verify Mesh Tree after reboot AP['%s']" % ap_ipaddr)
        self._verify_aps_info()
        if self.errmsg: return
        if self.passmsg: 
            self.passmsg = "Mesh Tree reformed correctly after reboot AP[%s] %s" % (ap_ipaddr, self.passmsg)

    def _test_reboot_zd(self):
        logging.info("Reboot Zone Director and verify Mesh Tree will not change after AP reboot")
        lib.zd.admin.reboot_zd(self.zd)

        logging.info("Verify Mesh Tree after reboot Zone Director")
        self._verify_aps_info()
        if self.errmsg: return
        if self.passmsg: 
            self.passmsg = "Mesh Tree reformed correctly after reboot ZD %s" % self.passmsg     