'''
Description:
    Remove the custom guest pass printout from ZD WebUI -> Configure -> Guest Access -> 
    Guest Pass Printout Customization table by name.
       
Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Remove_GuestPass_Printout_By_Name(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        logging.info("Remove guest pass printout: %s" % self.conf['gprint_name_list'])
        try:
            ga.remove_guestpass_printout(self.zd, self.conf['gprint_name_list'])
            self.passmsg = "Remove guest pass printout[%s] successfully" % self.conf['gprint_name_list']
            
        except Exception, e:
            errmsg = "Remove guest pass printout[%s] failed: %s"
            self.errmsg = errmsg % (self.conf['gprint_name_list'], e.message)
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
            
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'gprint_name_list': []}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.passmsg = ''
        self.errmsg = ''
        
    def _retrieve_carribag(self):
        pass
        
    def _update_carribag(self):
        pass
