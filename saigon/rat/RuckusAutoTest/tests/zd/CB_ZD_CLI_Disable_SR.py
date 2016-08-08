'''
Created on 2011-2-15
@author: louis.lou@ruckuswireless.com
description:

'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr

class CB_ZD_CLI_Disable_SR(Test):
    '''
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.errmsg = sr.set_no_sr(self.zdcli)
        
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
                         
                         )
        
        self.conf.update(conf)
                
        #@author: chentao @2013-08-29  to support ZD_SR testbed
        if self.conf.has_key('target_zd') and self.conf['target_zd']:
            if self.conf['target_zd'] == 'zd1':
                self.zdcli = self.testbed.components['ZDCLI1']
            elif self.conf['target_zd'] == 'zd2':
                self.zdcli = self.testbed.components['ZDCLI2'] 
            else:
                self.zdcli = self.carrierbag[self.conf['target_zd']]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        #@author: chentao @2013-08-29  to support ZD_SR testbed   
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         