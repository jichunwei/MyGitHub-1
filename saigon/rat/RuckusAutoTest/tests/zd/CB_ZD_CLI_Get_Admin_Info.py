'''
Description: Get Admin info from ZDCLI.
Created on 2010-10-27
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import admin as lib

class CB_ZD_CLI_Get_Admin_Info(Test):
    '''
    Get Admin info from ZDCLI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        try:
            if self.carrierbag.has_key('existed_admin_cfg'):
                admin_info = self.carrierbag['existed_admin_cfg']
            else:
                admin_info = lib.get_admin_info(self.zdcli)
                admin_info['admin_pass1'] = self.zdcli.password
                
            self._update_carrier_bag(admin_info)            
            
        except Exception, e:
            logging.warning(e.message)
            return self.returnResult('FAIL', e.message)
        
        return ["PASS", 'Show admin information correctly']
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self, admin_info):
        self.carrierbag['zdcli_admin_info'] = admin_info
        
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    