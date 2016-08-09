'''
Description:
    remote_ap_cli  -A "reboot" == > reboot all ap via remote_ap_cli command.

Notes:
    This API limitation, just support couple APs in the ZD, sometimes, AP can't response in time
    will result in failure counter !=0
    
Create on 2013-9-4
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test


class CB_ZD_CLI_Reboot_All_AP(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info("Try to reboot all AP via ap_remote_cli")
        msg = self.zdcli.do_shell_cmd("remote_ap_cli  -A 'reboot'")        
        if 'failure: 0' in msg:            
            return self.returnResult('PASS', "remote_ap_cli -A 'reboot' successful.")
        else:
            return self.returnResult('FAIL', msg)
    
    def cleanup(self):
        self._update_carribag()