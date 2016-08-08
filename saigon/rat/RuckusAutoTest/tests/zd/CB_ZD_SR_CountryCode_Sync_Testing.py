'''
Description:
Created on 2010-7-6
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_SR_CountryCode_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._test_country_code_sync()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        
        self.passmsg = 'country code changed can synchronize to standby zd correctly'
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
        
            
    def _test_country_code_sync(self):
        old_country_code = self.active_zd.get_country_code()
        self.active_zd.set_country_code()        
        a_country_code = self.active_zd.get_country_code()
        self._refresh_standby_zd()
        s_country_cde = self.standby_zd.get_country_code()
        if a_country_code != s_country_cde:
            self.errmsg = 'active ZD country code [%s] is different with standby ZD country code [%s]' % (a_country_code, s_country_cde)
            logging.warning(self.errmsg)
            return False
        self.passmsg = 'active ZD country code [%s] has synchronized to standby ZD' % a_country_code
        logging.info(self.passmsg)
        
        self.active_zd.set_country_code(old_country_code['label'])
        a_country_code = self.active_zd.get_country_code()
        self._refresh_standby_zd()
        s_country_code = self.standby_zd.get_country_code()
        if a_country_code != s_country_code:
            self.errmsg = 'active ZD country code [%s] is different with standby ZD country code [%s]' % (a_country_code, s_country_cde)
            logging.warning(self.errmsg)
            return False        
        self.passmsg = 'active ZD country code [%s] has synchronized to standby ZD' % a_country_code
        logging.info(self.passmsg)
        
        return True   