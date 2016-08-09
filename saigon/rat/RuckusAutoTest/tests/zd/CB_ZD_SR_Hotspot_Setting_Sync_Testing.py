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

class CB_ZD_SR_Hotspot_Setting_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_hotspot_setting_sync()
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
        
            
    def _test_hotspot_setting_sync(self):
        h_cfg = {
            'name': 'rat-hotspot-test',
            'login_page': 'http://192.168.0.250/login.html',             
            }
        lib.zd.wispr.create_profile(self.active_zd, **h_cfg)
        a_h_cfg = lib.zd.wispr.get_profile_by_name(self.active_zd, h_cfg['name'])
        self._refresh_standby_zd()
        s_h_cfg = lib.zd.wispr.get_profile_by_name(self.standby_zd, h_cfg['name'])
        if not self._verify_dict(a_h_cfg, s_h_cfg):
            return False
        
        self.passmsg = 'Created hotspot profile has synchronized to standby ZD'
        logging.info(self.passmsg)
        old_name = h_cfg['name']
        h_cfg['name'] = 'rat-hotspot-test-edit'
        h_cfg['login_page'] = 'http://192.168.0.250/slogin.html'
        lib.zd.wispr.cfg_profile(self.active_zd, old_name, **h_cfg)
        a_h_cfg = lib.zd.wispr.get_profile_by_name(self.active_zd, h_cfg['name'])
        self._refresh_standby_zd()
        s_h_cfg = lib.zd.wispr.get_profile_by_name(self.standby_zd, h_cfg['name'])
        if not self._verify_dict(a_h_cfg, s_h_cfg):
            return False
        
        self.passmsg = 'Modified hotspot profile has synchronized to standby ZD'
        logging.info(self.passmsg)
        
        lib.zd.wispr.remove_all_profiles(self.active_zd)
        try:
            a_h_cfg = lib.zd.wispr.get_profile_by_name(self.active_zd, h_cfg['name'])
            self.errmsg = 'profile [%s] has not deleted in active ZD' % h_cfg['name']
            logging.warning(self.errmsg)
            return False            
        except:
            pass
        
        try:
            self._refresh_standby_zd()            
            s_h_cfg = lib.zd.wispr.get_profile_by_name(self.standby_zd, h_cfg['name'])
            self.errmsg = 'deleted profile [%s] has not been synchronized to standby ZD' % h_cfg['name']
            logging.warning(self.errmsg)
            return False                        
        except:
            pass
        
        self.passmsg = 'Deleted hotspot profile has synchronized to standby ZD'
        logging.warning(self.passmsg)        
        return True
        
    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True        
        
        