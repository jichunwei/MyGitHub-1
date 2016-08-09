'''
Description:
    Remove guest pass from ZD WebUI -> Monitor -> Generated Guest Passes table by the guest name.
       
Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Remove_GuestPass_By_GuestName(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            logging.info("Delete the guest passes of '%s'" % self.guest_name)
            ga.delete_guestpass(self.zd, self.guest_name, self.conf['load_time'])
            
            logging.info("Make sure the entry disappears from the table")
            ga.get_guestpass_by_name(self.zd, self.guest_name)
            self.errmsg = "The guest pass %s still exists in the table" % self.guest_name

        except Exception, e:
            if 'No matched row found' in e.message:
                self.passmsg = "The guest passes of '%s' disappeared from the table" % self.guest_name

            else:
                self.errmsg = "Delete the guest passes of '%s' failed: %s" % (self.guest_name, e.message)
                
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
            
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'guest_name': '',
                     'load_time': 2,
                     }
        self.conf.update(conf)
        
        self.guest_name = self.conf['guest_name']
        self.zd = self.testbed.components['ZoneDirector']
        self.passmsg = ''
        self.errmsg = ''
        
    def _retrieve_carribag(self):
        if not self.guest_name:
            self.guest_name = self.carrierbag['single_gp']['guest_name']
        
    def _update_carribag(self):
        pass
