'''
Description:
Created on 2010-7-2
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_SR_Guest_Access_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        res = self._test_guest_access_setting_sync()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        
        self.passmsg = 'Enable/Edit/Disable guestaccess setting can be synchronized to standby zd.'
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
        
    
    def _test_guest_access_setting_sync(self):
        #@author: Anzuo
        g_a_cfg = dict(use_guestpass_auth = True,
                       onboarding_portal = True,
                       #enable_share_guestpass = True,
                       use_tou = True,
                       redirect_url = 'http://www.example.net/')
        self.active_zd.set_guestaccess_policy(**g_a_cfg)
        
        res = self._verify_guest_access_setting(g_a_cfg)
        if not res:
            return False
        
        self.passmsg = 'Enable guestaccess setting can synchronized to standby zd.'
        logging.info(self.passmsg)
        
        g_a_cfg['use_tou'] = False
        g_a_cfg['redirect_url'] = ''
        self.active_zd.set_guestaccess_policy(**g_a_cfg)
        res = self._verify_guest_access_setting(g_a_cfg)
        if not res:
            return False
        self.passmsg = 'Edit guestaccess setting can synchronized to standby zd.'
        logging.info(self.passmsg)
        
        g_a_cfg['use_guestpass_auth'] = False
        self.active_zd.set_guestaccess_policy(**g_a_cfg)
        res = self._verify_guest_access_setting(g_a_cfg)
        if not res:
            return False
        self.passmsg = 'Disable guestaccess setting can synchronized to standby zd.'
        logging.info(self.passmsg)
        
        return True
            
    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass  
        
                    
    def _verify_guest_access_setting(self, g_a_cfg):
        active_g_a_cfg = self.active_zd.get_guestaccess_policy()
        res = self._verify_dict(g_a_cfg, active_g_a_cfg)
        if not res:
            return False
        self._refresh_standby_zd()
        standby_g_a_cfg = self.standby_zd.get_guestaccess_policy()
        res = self._verify_dict(active_g_a_cfg, standby_g_a_cfg)
        if not res:
            return False
    
    
    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True
             
        
