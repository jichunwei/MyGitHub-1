'''
Description:
Created on 2010-7-5
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_SR_Roles_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_roles_cfg_sync()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        
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

    def _test_roles_cfg_sync(self):
        r_cfg_1 = {"rolename": "rat-role-test-1", "specify_wlan": "", "guestpass": True, "description": "",
                "group_attr": "", "zd_admin": ""}        
        r_cfg_2 = {"rolename": "rat-role-test-2", "specify_wlan": "", "guestpass": True, "description": "",
                "group_attr": "", "zd_admin": ""}
        self.active_zd.create_role(**r_cfg_1)
        self.active_zd.create_role(**r_cfg_2)
        
        r_name_list = [r_cfg_1['rolename'], r_cfg_2['rolename']]
        res = self._verify_roles_cfg(r_name_list)
        if not res:
            return False
        else:
            self.passmsg = "Create/Edit/Delete roles can synchronized to standby zd."
            return True
        
    def _verify_roles_cfg(self, r_name_list):
        a_r_name_list = self.active_zd.get_role()
        if not self._verify_list(r_name_list, a_r_name_list):
            return False
        else:
            logging.info('roles [%s] have been created successfully' % r_name_list)
            
        s_r_name_list = self.standby_zd.get_role()
        if not self._verify_list(a_r_name_list, s_r_name_list):
            return False
        else:
            logging.info('roles [%s] have been synchronized to standby zd' % s_r_name_list)
        
        self.active_zd.remove_all_roles(r_name_list[0])
        a_r_name_list = self.active_zd.get_role()
        s_r_name_list = self.standby_zd.get_role()
        if not self._verify_list(a_r_name_list, s_r_name_list):
            return False
        else:
            logging.info('roles [%s] have been synchronized to standby zd' % a_r_name_list)
        
        self.active_zd.remove_all_roles()
        a_r_name_list = self.active_zd.get_role()
        s_r_name_list = self.standby_zd.get_role()
        if not self._verify_list(a_r_name_list, s_r_name_list):
            return False
        else:
            logging.info('Deleted roles have synchronized to standby zd')
        
                                    
    
    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True
    
    def _verify_list(self, target = [], source = []):
        for name in target:
            if not source.__contains__(name):
                self.errmsg = 'role [%s] has been created' % name
                logging.warning(self.errmsg)
                return False
                
        return True    
        
                        
    
