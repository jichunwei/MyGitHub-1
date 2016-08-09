'''
Created on 2013-09-22
@author: ye.songnan@odc-ruckuswireless.com
description:
    Enable bonjour gateway.
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import bonjour_gateway as bg

class CB_ZD_CLI_Enable_Bonjour_Gateway(Test):
    '''
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        res = bg.enable_bonjour_gateway(self.zdcli)
        if self.tag_nagative:
            if "Mdnsproxy is successfully started." not in res['mdnsproxy zd'][0]:
                self.passmsg = 'Shoud enable bonjour gateway failed, and it did.'
            else:
                self.errmsg = 'Shoud enable bonjour gateway failed, but it did not.'  
        else:
            if "Mdnsproxy is successfully started." in res['mdnsproxy zd'][0]:
                self.passmsg = 'Enable bonjour gateway successfully.'
            else:
                self.errmsg = 'Enable bonjour gateway failed.' 
                                   
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         tag_nagative = False
                         )
        
        self.conf.update(conf)
        self.tag_nagative = self.conf['tag_nagative']
                
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass 
    
      