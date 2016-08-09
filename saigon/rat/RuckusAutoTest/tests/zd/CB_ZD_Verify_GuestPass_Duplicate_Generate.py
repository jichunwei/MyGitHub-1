'''
Description:
    Verify duplicated guest name and guest pass can not be imported to ZD. 
       
Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Verify_GuestPass_Duplicate_Generate(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            zd_url = self.zd.selenium_mgr.to_url(self.zd.ip_addr, self.zd.https)
            dlg_text_dupgp = 'The key %s already exists. Please enter a different key'
            self.conf.update({'dlg_title': "The page at %s says:" % zd_url,
                              'dlg_text': dlg_text_dupgp % self.conf['key']
                              }) 
        
            logging.info('try to generate another guest pass using the key has been generated')
            ga.generate_guestpass(self.zd, **self.conf)

        except Exception, e:
            if "Please enter a different key" in e.message:
                self.passmsg = "Duplicated guest pass cannot be used is confirmed"

            else:
                self.errmsg = "Unable to verify duplicated guest pass generation: %s" % e.message
                
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
            
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'type': 'single',
                     'guest_fullname': '',
                     'duration': '',
                     'duration_unit': '',
                     'wlan': '',
                     'remarks': '',
                     'key': '',
                     'is_shared': 'No',
                     'auth_ser': 'Local Database',
                     'username': '',
                     'password': '',
                     }
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.passmsg = ''
        self.errmsg = ''
        
    def _retrieve_carribag(self):
        if not self.conf['guest_fullname']:
            self.conf['guest_fullname'] = self.carrierbag['single_gp']['guest_name']
        
        if not self.conf['key']:
            self.conf['key'] = self.carrierbag['single_gp']['guest_pass']
        
    def _update_carribag(self):
        pass
