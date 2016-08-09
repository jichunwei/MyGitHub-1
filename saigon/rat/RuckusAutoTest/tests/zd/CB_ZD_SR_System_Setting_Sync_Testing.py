'''
Description:
Created on 2010-7-8
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_SR_System_Setting_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_system_setting_sync()
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
        

    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass  
                
    
    def _test_system_setting_sync(self):
        orignal_name = self.active_zd.get_system_name()
        test_name = "rat-system-name-sync"
        self.active_zd.set_system_name(test_name)
        a_s_name = self.active_zd.get_system_name()
        self._refresh_standby_zd()
        s_s_name = self.standby_zd.get_system_name()
        if a_s_name != s_s_name:
            self.errmsg = 'system name [%s] has not synchronized to standby ZD' % a_s_name
            return False
        
        self.passmsg = 'system name has synchronized to standby zd'
        logging.info(self.passmsg)
        
        self.active_zd.set_system_name(orignal_name)
        return True
        
    
