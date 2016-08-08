"""
   Description: 
   This test class support to verify the neighbour APs list
   @since: Jun 2013
   @author: An Nguyen

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the DHCP lease time of special station from AP and check the lease time      
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Verify DHCP lease time on AP success 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_AP_CLI_Verify_Neighbour_AP_List(Test):
    required_components = ['RuckusAP','Station']
    parameters_description = {'expected_neighbour_ap': [],
                              'ap_tag' : 'active_ap',
                              'negative': False
                              }

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self._verify_neighbour_ap_list()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'expected_neighbour_ap': [],
                     'ap_tag' : 'active_ap',
                     'negative': False
                     }
        
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
   
    def _verify_neighbour_ap_list(self):
        logging.info('Verify the neighbour APs list on AP %s' % self.active_ap.base_mac_addr)
        val = lib.apcli.radiogrp.get_mesh_list(self.active_ap)
        if not val.get('N'):
            if not self.conf['negative']:
                self.errmsg = '[INCORRECT BEHAVIOR] There is not any neighbour AP is recorded'
            else:
                self.passmsg = '[CORRECT BEHAVIOR] There is not any neighbour AP is recorded'
            return
        
        if self.conf['negative']:
            self.errmsg = '[INCORRECT BEHAVIOR] Neighbour AP %s is recorded' % val['N'].keys()
            return
        
        logging.info('The neighbour APs list: \n%s' % val['N'])
        error_mac = []
        for mac in self.conf['expected_neighbour_ap']:
            if mac.lower() not in val['N'].keys():
                error_mac.append(mac)
        
        if error_mac:
            self.errmsg = '[INCORRECT BEHAVIOR] The APs %s are not shown in neighbour AP list' % error_mac
        else:
            msg = '[CORRECT BEHAVIOR] The APs %s are shown in neighbour AP list as expected'
            self.passmsg = msg % self.conf['expected_neighbour_ap']