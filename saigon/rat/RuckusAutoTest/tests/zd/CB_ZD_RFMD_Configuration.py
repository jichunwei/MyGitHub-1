"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tann@ruckuswireless.com
   @since: August 2012

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

default_thresh = '2'

class CB_ZD_RFMD_Configuration(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        ap_list = [self.root_ap, self.mesh_ap_1, self.mesh_ap_2]
        for ap in ap_list:
            ap.set_rfmd_option(False)
            self.verify_all_ap_status_after_rfmd(ap_list)

            ap.set_rfmd_option(True)
            value = ap.get_radar_threshold()
            if value != default_thresh:
                self.errmsg += 'Default threshold value of AP[%s] is not %s' % (ap.base_mac_addr, default_thresh)
            
            new_val = '6'
            ap.set_radar_threshold(new_val)
            ap.get_radar_threshold()
            value = ap.get_radar_threshold()
            if value != new_val:
                self.errmsg += 'Modify threshold value of AP[%s] to %s failure' % (ap.base_mac_addr, new_val)

            ap.set_radar_threshold(default_thresh)
            time.sleep(5)#60s
            self.verify_all_ap_status_after_rfmd(ap_list)
            
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {}
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
        self.test_dfs_channel = ''
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.root_ap   = self.carrierbag[self.conf['root_ap']]['ap_ins']
        self.mesh_ap_1 = self.carrierbag[self.conf['mesh_ap_1']]['ap_ins']
        self.mesh_ap_2 = self.carrierbag[self.conf['mesh_ap_2']]['ap_ins']
        
    def verify_all_ap_status_after_rfmd(self, ap_list):
        for ap in ap_list:
            ap_info= lib.zd.aps.get_ap_brief_by_mac_addr(self.zd, ap.base_mac_addr)
            if not ap_info['state'].lower().startswith('connected'):
                self.errmsg += 'AP[%s] disconnect from ZD after RFMD radar detected' % ap.base_mac_addr
