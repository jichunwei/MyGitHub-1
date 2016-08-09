"""
   Description: 
   This test class support to verify the 80211debug message for the background scanning
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

class CB_AP_CLI_Verify_Background_Scanning_Message(Test):
    required_components = ['RuckusAP','Station']
    parameters_description = {'expected_msg': 'apmgr',
                              'ap_tag' : 'active_ap',
                              'verify_time' : 120,
                              'negative': False}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self._verify_background_scanning_message()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'expected_msg': 'apmgr',
                     'ap_tag' : 'active_ap',
                     'scan_interval' : 20,
                     'negative': False,
                     'expected_number': 5}
        
        self.conf.update(conf)
        self.expected_msg_contain = 'active scan request from'
        self.expected_msg_type = 'ieee80211_ioctl_siwscan'
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
   
    def _verify_background_scanning_message(self):
        logging.info('Verify the background scanning log on AP %s' % self.active_ap.base_mac_addr)
        expected_number = self.conf['expected_number'] if not self.conf['negative'] else 0        
        verifying_time = 30*expected_number if self.conf['expected_msg'] == 'meshd' else self.conf['scan_interval']*expected_number
        logmsgs = lib.apcli.shell.read_comming_log(self.active_ap, self.conf['expected_msg'], verifying_time)
        logging.info('Reading logs results: \n%s' % logmsgs)
        scanmsg = []
        for logmsg in logmsgs:
            val = logmsg.split(': ')
            if len(val) < 4:
                continue
            if val[-2] == self.expected_msg_type and self.expected_msg_contain in val[-1]:
                scanmsg.append(val)
        if len(scanmsg) < int(expected_number) - 1 or len(scanmsg) > int(expected_number) + 1:
            msg = '[INCORRECT BEHAVIOR] There are(is) %s "%s %s" msgs recorded instead of %s as expected'
            self.errmsg = msg % ((len(scanmsg), self.expected_msg_contain, self.conf['expected_msg'], expected_number))
            return
        
        msg = '[CORRECT BEHAVIOR] There are(is) %s "%s %s" recorded as expected'
        self.passmsg = msg % (len(scanmsg), self.expected_msg_contain, self.conf['expected_msg'])