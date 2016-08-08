"""
   Description: 
   This test class support to verify the configure the device policy by ZDCLI
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

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Configure_Device_Policy(Test):
    required_components = ['RuckusAP','Station']
    parameters_description = {'device_policy_list': [{}],
                              'negative': False}

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        self._verify_configurating_device_policy()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'device_policy_list': [],
                     'negative': False,
                     'waiting_time': 30}
        
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _verify_configurating_device_policy(self):
        logging.info('Verify to configure device policy')
        errmsg = ''
        passmsg = ''
        if not self.conf['device_policy_list']:
            raise Exception('There is not any device policy to configure. Please check!')
        for pol in self.conf['device_policy_list']:
            res, msg = lib.zdcli.dvccfg.configure_device_policy(self.zdcli, pol)
            logging.debug(msg)
            if res:
                passmsg += 'Passed to configure device policy %s. ' % pol['name']
            else:
                errmsg += 'Failed to configure device policy %s. ' % pol['name']
        
        logging.info('Waiting %s seconds for the new configuration is update to APs' % self.conf['waiting_time'])
        time.sleep(self.conf['waiting_time'])
        
        if errmsg and self.conf['negative']:
            self.passmsg = '[CORRECT BEHAVIOR] %s' % errmsg
        elif errmsg and not self.conf['negative']:
            self.errmsg = '[INCORRECT BEHAVIOR] %s' % errmsg
        elif not errmsg and self.conf['negative']:
            self.errmsg = '[INCORRECT BEHAVIOR] %s' % passmsg
        else:
            self.passmsg = '[CORRECT BEHAVIOR] %s' % passmsg      
        