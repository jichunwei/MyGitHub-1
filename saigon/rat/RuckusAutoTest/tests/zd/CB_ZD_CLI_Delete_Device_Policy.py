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

class CB_ZD_CLI_Delete_Device_Policy(Test):
    required_components = ['RuckusAP','Station']
    parameters_description = {'device_policy_name_list': [{}],
                              'negative': False}

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        self._verify_delete_device_policy()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'device_policy_name_list': [],
                     'negative': False,
                     'waiting_time': 30}
        
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _verify_delete_device_policy(self):
        logging.info('Verify to delete device policy')
        errmsg = ''
        passmsg = ''
        if not self.conf['device_policy_name_list']:
            msg = 'The parameter "device_policy_name_list" is empty. All Device Policies will be delete!'
            logging.info(msg)
            res = lib.zdcli.dvccfg.delete_all_device_policies(self.zdcli)
        else:
            msg = 'The device policies %s will be deleted.' % self.conf['device_policy_name_list']
            logging.info(msg)
            res = lib.zdcli.dvccfg.delete_device_policies(self.zdcli, self.conf['device_policy_name_list'])
        
        fail_res = {}
        for cmd_res in res.keys():
            if 'cannot be deleted' in res[cmd_res]:
                fail_res[cmd_res] = res[cmd_res]
        
        if not fail_res:            
            passmsg += 'Passed to delete device policy %s' % res
        else:
            errmsg += 'Failed to configure device policy %s' % fail_res
        
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
        