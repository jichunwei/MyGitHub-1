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
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_SR_Alarm_Setting_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_alarm_setting_sync()
        if self.errmsg:
            return('FAIL', self.errmsg)
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
        self.conf = {'check_status_timeout':120,}
        self.conf['alarm_setting'] = dict(
            email_addr = 'lab@example.net', 
            server_name = '192.168.0.252', 
            server_port = '25', 
            username = 'lab', 
            password = 'lab4man1',
            tls_option = False, 
            starttls_option = False
        )
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass  
                
    
    def _test_alarm_setting_sync(self):
        try: 
            lib.zd.asz.set_alarm_email(self.active_zd,self.conf['alarm_setting']['email_addr'], 
                                                      self.conf['alarm_setting']['server_name'], 
                                                      self.conf['alarm_setting']['server_port'], 
                                                      self.conf['alarm_setting']['username'], 
                                                      self.conf['alarm_setting']['password'], 
                                                      self.conf['alarm_setting']['tls_option'], 
                                                      self.conf['alarm_setting']['starttls_option'])
        except Exception, e: 
            self.errmsg = e.message
            return self.returnResult('FAIL', self.errmsg)
        a_a_cfg = self.active_zd.get_alarm_email()
        
        self._refresh_standby_zd()
        s_a_cfg = self.standby_zd.get_alarm_email()
        if not self._verify_dict(a_a_cfg, s_a_cfg):
            return False
        self.passmsg = 'Alarm mail setting has synchronized to standby ZD'
        logging.info(self.passmsg)
        lib.zd.asz.clear_alarm_settings(self.active_zd)
        return True
        


    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True     
            

    
