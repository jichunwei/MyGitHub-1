'''
Description:
    Set country code from ZD CLI, and make sure:
        1) All of AP are reconnected.
        2) ZD Countrycode has been updated.
Create on 2013-5-8
@author: cwang@ruckuswireless.com
'''

import logging
import time
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components import Helpers

class CB_ZD_CLI_Set_AP_CountryCode(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(cc='US',
                         ccalias = 'United states',
                         chk_ap = True,
                         )
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.zd = self.testbed.components['ZoneDirector']        
        self.cc = self.conf.get('cc')
        self.ccalias = self.conf.get('ccalias')
        self.chk_ap = self.conf.get('chk_ap')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Set Country Code %s' % self.cc)
        try:
            Helpers.zdcli.system.dot11_country_code(self.zdcli, self.cc)
        except Exception, e:
            import traceback
            logging.debug(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
        
        
        logging.info('Get Country Code information from config>>system')
        try:        
            CODE  = Helpers.zdcli.system.get_country_code(self.zdcli)
            # @author:Chico, @change: format standard, @bug: ZF-9159
            if CODE.lower()  != self.ccalias.lower():
            # @author:Chico, @change: format standard, @bug: ZF-9159
                return self.returnResult('FAIL', 
                                         "Expected country code %s, actual %s" % 
                                         (self.ccalias, CODE))
            
        except Exception, e:
            logging.debug(traceback.format_exc())
            return self.returnResult('FAIL', e.message)   
    
        if self.chk_ap:
            st = time.time()
            while time.time() - st < 120:
                logging.info('Wait for AP re-join.')
                time.sleep(20)
                self.aps = self.zd.get_all_ap_info()
                apnum = len(self.aps)
                logging.info('Check AP if connected and country code if set correctly.')
                for ap in self.aps:
                    if 'connected' in ap['status'].lower():
#                        ap_mac_addr = ap['mac']
                        ipaddr = ap['ip_addr']
                        for apins in self.testbed.components['AP']:
                            if apins.get_ip_addr() == ipaddr:
                                code = apins.get_country_code()
                                if code != self.cc:
                                    return self.returnResult('FAIL',
                                                             'AP%s Country Code set is %s, expected %s' 
                                                             % (ipaddr, code, self.cc))
                        apnum = apnum - 1
                    else:
                        break
                
            if apnum:
                return self.returnResult('FAIL', 
                                         'Some APs still are disconnected, please check')                
                        
        
        return self.returnResult('PASS', 'Set Country Code %s DONE' % self.cc)
    
    def cleanup(self):
        self._update_carribag()