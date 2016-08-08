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
from RuckusAutoTest.components.lib.zd import user

class CB_ZD_SR_User_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_users_cfg_sync()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        self.passmsg = 'Create/Edit/Delete user can be synchronized to standby zd.'
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
                
    
    def _test_users_cfg_sync(self):
        cfg = {
            'username': 'ras.user.test',
            'fullname': 'ras.user.test',
            'password': 'ras.user.test',
            'confirm_password': 'ras.user.test',
            'role': 'Default',
            'number': 1
            }
        user.create_user(self.active_zd, cfg)
        res = self._verify_user_cfg(cfg)
        if not res:
            return False
        
        oldname = cfg['username']
        cfg['username'] = 'ras.user.test.edit'
        cfg['fullname'] = 'ras.user.test.edit'
        cfg.pop('number')
        user.edit_user(self.active_zd, oldname, cfg)
        res = self._verify_user_cfg(cfg)
        if not res:
            return False
        
        user.delete_user(self.active_zd, cfg['username'])        
        a_user_cfg = user.get_user(self.active_zd, cfg['username'])
        if a_user_cfg:
            self.errmsg = "user [%s] has not deleted succesfully" % cfg['username']
            return False
        
        self._refresh_standby_zd()
        s_user_cfg = user.get_user(self.standby_zd, cfg['username'])
        if not s_user_cfg:
            self.passmsg = 'deleted user [%s] has synchronized to standby zd' % cfg['username']
            logging.info(self.passmsg)
                    
        else:
            self.errmsg = 'deleted user [%s] has not synchronized to standby zd, existed in standby zd' % cfg['username']
            logging.warning(self.errmsg)
        
        
    def _verify_user_cfg(self, cfg):
        active_user_cfg = user.get_user(self.active_zd, cfg['username'])
        self._refresh_standby_zd()
        standby_user_cfg = user.get_user(self.standby_zd, cfg['username'])
        if not active_user_cfg:
            self.errmsg = "user [%s] has not created successfully" % cfg['username']
            logging.warning(self.errmsg)
            return False
         
        if not standby_user_cfg:
            self.errmsg = "user [%s] has not synchronized to standby zd" % cfg['username']
            logging.warning(self.errmsg)
            return False
        
        else:
            if cfg['fullname'] != standby_user_cfg['fullname']\
                or cfg['role'] != standby_user_cfg['role']:
                self.errmsg = 'user cfg [%s] of active zd is different from standby zd [%s]' % (cfg, standby_user_cfg)
                logging.warning(self.errmsg)
                return False
        
        self.passmsg = "user cfg has synchronized to standby zd correctly."
        logging.info(self.passmsg)
        return True
        
        
