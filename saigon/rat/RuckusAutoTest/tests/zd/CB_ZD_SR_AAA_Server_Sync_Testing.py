'''
Description:
Created on 2010-7-7
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_SR_AAA_Server_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_aaa_server_sync()
        if self.errmsg:
            return('FAIL', self.errmsg)
        
        self.passmsg = 'Create/Delete AAA server has been synchronized to standby ZD successfully'
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']        
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''


    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass  
        
            
    def _test_aaa_server_sync(self):
        server_cfg = {'server_addr': '192.168.0.252', 'server_port': '1812', 'server_name': 'radius_server',
                      'win_domain_name': '', 'ldap_search_base': '',
                      'ldap_admin_dn': '', 'ldap_admin_pwd': '',
                      'radius_auth_secret': '1234567890', 'radius_acct_secret': ''}
        
        lib.zd.aaa.create_server(self.active_zd, **server_cfg)
        a_s_cfg_list = lib.zd.aaa.get_auth_server_info_list(self.active_zd)
        self._refresh_standby_zd()
        s_s_cfg_list = lib.zd.aaa.get_auth_server_info_list(self.standby_zd)
        size = len(a_s_cfg_list)
        for i in range(size):
            if not self._verify_dict(a_s_cfg_list[i], s_s_cfg_list[i]):
                return False
        self.passmsg = 'Created server [%s] has synchronized to standby zd' % server_cfg['server_name']
        logging.info(self.passmsg)
        
        lib.zd.aaa.remove_all_servers(self.active_zd)
        a_s_cfg_list = lib.zd.aaa.get_auth_server_info_list(self.active_zd)
        self._refresh_standby_zd()
        s_s_cfg_list = lib.zd.aaa.get_auth_server_info_list(self.standby_zd)
        if a_s_cfg_list:
            self.errmsg = 'AAA Servers have not been deleted correctly'
            return False
        if s_s_cfg_list:
            self.errmsg = 'Deleted AAA servers have not been synchronized to standby ZD'
            return False
        
        self.passmsg = 'Deleted AAA servers have been synchronized to standby ZD'
        logging.info(self.passmsg)
        return True 

    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True        
        
    
