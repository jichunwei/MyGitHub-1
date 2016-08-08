'''
Description:
    Generate multiple guest passes by import CSV profile.
       
Create on 2011-8-23
@author: serena.tan@ruckuswireless.com
'''


import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Generate_Multi_GuestPass_By_CSV_Profile(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        logging.info("Import CSV file [%s] to generate guest passes" % self.batch_file.name)
        try:
            ga.generate_guestpass(self.zd, **self.conf)
            passmsg = 'Generate guest passes by CSV file [%s], server [%s] successfully'
            self.passmsg = passmsg % (self.batch_file.name, self.conf['auth_ser'])
            
        except Exception, e:
            errmsg = 'Generate guest passes by CSV file [%s] failed: %s'
            self.errmsg = errmsg % (self.batch_file.name, e.message)
        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'is_shared': 'No',
                     'auth_ser': 'Local Database',
                     'username': '',
                     'password': '',
                     'type': 'multiple',
                     'duration': '',
                     'duration_unit': '',
                     'wlan': '',
                     }
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        self.batch_file = self.carrierbag['gp_cfg']['profile_file']
        self.conf['profile_file'] = '\\'.join((os.getcwd(), self.batch_file.name))
  
    def _update_carribag(self):
        pass
