'''
Description:Verify WLAN, User, AAA, Role are empty from WEBUI.
Created on 2010-8-4
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib 

class CB_Scaling_Verify_Empty_CFG(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        errmsg = []
        self._check_local_user_empty()
        if self.errmsg:
            errmsg.append(self.errmsg)
            logging.warning(self.errmsg)
        
        self._check_role_empty_beyond_default()
        if self.errmsg:
            errmsg.append(self.errmsg)
            logging.warning(self.errmsg)
        
        self._check_aaa_empty()
        if self.errmsg:
            errmsg.append(self.errmsg)
            logging.warning(self.errmsg)
        
        self._check_wlan_empty()
        if self.errmsg:
            errmsg.append(self.errmsg)
            logging.warning(self.errmsg)
        
        if errmsg:
            return self.returnResult("FAIL", errmsg)
        self._update_carrier_bag()
        self.passmsg = 'User, Role, AAA, WLANs are empty'
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _check_local_user_empty(self):
        current_user_list = self.zd.get_user()
        if current_user_list:
            self.errmsg = 'Current ZD contains users [%s],' % current_user_list
    
    def _check_role_empty_beyond_default(self):
        cnt = self.zd._get_total_role_entries()
        if cnt > 1:
            self.errmsg += 'Current ZD contains more than 1 roles,'
    
    def _check_aaa_empty(self):
        current_aaa_list = lib.zd.aaa.get_auth_server_info_list(self.zd)
        if current_aaa_list:
            self.errmsg = 'Current ZD contains AAA [%s],' % current_aaa_list
    
    def _check_wlan_empty(self):
        current_wlan_list = lib.zd.wlan.get_wlan_list(self.zd)
        if current_wlan_list:
            self.errmsg = 'Current ZD contains WLANs [%s],' % current_wlan_list
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']   
        if self.conf.has_key('zd') and self.conf['zd']=='standby_zd' and self.carrierbag.has_key('standby_zd'):
            self.zd = self.carrierbag['standby_zd']  
            
        self.errmsg = ''
        self.passmsg = ''
    
