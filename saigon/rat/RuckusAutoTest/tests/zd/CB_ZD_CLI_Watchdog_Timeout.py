'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirectorCLI'
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
        
        
Create on 2013-2-27
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.common.sshclient import sshclient

from RuckusAutoTest.models import Test

class CB_ZD_CLI_Watchdog_Timeout(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'timeout':600,}
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.timeout = self.conf.get('timeout')
        self.passmsg = ""
        self.errormsg = ""
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self.zdcli.do_shell_cmd("killall -9 wd_feeder")
            time.sleep(30)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        logging.info('Reboot after watchdog be killed')        
        time_start=time.time()        
        came_back=False
        
        while time.time() - time_start < self.timeout:
            time.sleep(5)
            try:
                self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, 
                                             self.zdcli.port,'admin','admin')
                self.zdcli.login()
                logging.warning(self.passmsg)
                came_back=True
                time.sleep(30)
                break 
            except:
                pass
            
                    
        if not came_back: 
            return self.returnResult("FAIL", 
                                     "time out when reconnect cli after reboot")            
        
        return self.returnResult('PASS', 'watchdog timeout testing.')
    
    def cleanup(self):
        self._update_carribag()