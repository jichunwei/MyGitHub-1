'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2012-2-15
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers
from RuckusAutoTest.common.sshclient import sshclient

class CB_ZD_Reboot(Test):
    required_components = ['ZoneDirector', 'ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli=self.testbed.components['ZoneDirectorCLI']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            Helpers.zd.admin.reboot_zd(self.zd)            
        except Exception, ex:
            logging.info('Reboot ZD failed, reason: '% ex.message)
            return self.returnResult('FAIL', ex.message)
        
        try:
            #@author: Jane.Guo @since: 2013-09 fix bug don't set session timeout
            self.zdcli.do_shell_cmd('',set_session_timeout=False)
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login(set_session_timeout=False)
            
        return self.returnResult('PASS', "Reboot Correctly")
    
    def cleanup(self):
        self._update_carribag()
