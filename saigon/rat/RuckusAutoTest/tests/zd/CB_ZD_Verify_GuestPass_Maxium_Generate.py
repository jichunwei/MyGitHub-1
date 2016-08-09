'''
Description:
    Verify the maximum guest passes generation.
       
Create on 2011-8-27
@author: serena.tan@ruckuswireless.com
'''


import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Verify_GuestPass_Maxium_Generate(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrieve_carribag()

    def test(self):
        ga._log_to_generate_guestpass_page(self.zd)
        time.sleep(2)
        
        idx, idx, total = ga._get_page_range_and_total_number_of_generated_guestpass(self.zd)
        total = int(total)
        
        while True:
            try:
                ga.generate_guestpass(self.zd, **self.conf)
                total += self.conf['number_profile']

            except Exception, e:
                if self.conf['dlg_text'] in e.message and \
                self.conf['max_gp_allowable'] - total < self.conf['number_profile']:
                    self.passmsg = '%s guest pass(es) were generated,' % total
                    self.passmsg += "ZD doesn't allow to generate more guest passes when maximum allowable size was reached."

                else:
                    self.errmsg = "Failed to generate or verify maximum number of guest passes: %s" % e.message

                break
        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'username': '',
                     'password': '',
                     'auth_ser': '',
                     'type': 'multiple',
                     'duration': '1',
                     'duration_unit': 'Days',
                     'wlan': '',
                     'remarks': '',
                     'key': '',
                     'number_profile': 100,
                     'max_gp_allowable': 1250,
                     }
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
            
        zd_url = self.zd.selenium_mgr.to_url(self.zd.ip_addr, self.zd.https)
        dlg_text_maxgp = "The total number of guest and user accounts reaches maximum allowable size %d"
        self.conf.update({'dlg_title': "The page at %s says:" % zd_url,
                          'dlg_text': dlg_text_maxgp % self.conf['max_gp_allowable']
                          })    
        
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        pass
  
    def _update_carribag(self):
        pass
