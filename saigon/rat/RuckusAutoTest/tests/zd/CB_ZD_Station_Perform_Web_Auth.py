'''
Description:
    Perform web auth action correctly against ZoneDirector.

Created on 2010-9-1
@author: cwang@ruckuswireless.com    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_ZD_Station_Perform_Web_Auth(Test):
    '''
    Perform web auth action correctly against ZoneDirector.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        logging.info("Perform Web authentication on the target station %s" % self.target_station.get_ip_addr())
        arg = tconfig.get_web_auth_params(self.zd, self.username, self.password)
        try:
            self.target_station.perform_web_auth(arg)
        except Exception, e:
            #try it again
            logging.warning(e)
            import time
            time.sleep(10)
            self.target_station.perform_web_auth(arg)
            
        self._update_carrier_bag()
        self.passmsg = "Perform Web authentication on the target station %s, succefully" % self.target_station.get_ip_addr()
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
        
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(username = 'ras.local.user',
                         password = 'ras.local.user',
                         sta_tag = '192.168.1.11',) #@since: 2013-7-29 @author: Jane.Guo, add a param to get station tag
        self.conf.update(conf)
        self.username = self.conf['username']
        self.password = self.conf['password']
        self.zd = self.testbed.components['ZoneDirector']
        try:
            self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        except:
            self.target_station = self.carrierbag['Station'][self.conf['sta_tag']]['sta_ins']        
        self.errmsg = ''
        self.passmsg = ''
    
