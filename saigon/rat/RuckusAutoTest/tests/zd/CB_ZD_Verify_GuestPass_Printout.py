'''
Description:
    Verify the guest pass printout.
    
Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Verify_GuestPass_Printout(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        logging.info("Verify guest pass printout")
        try:
            ga._verify_guestpass_printout(self.zd, self.guest_pass, **self.printout_cfg)
            self.passmsg = "Verify guest pass printout successfully"
            
        except Exception, e:
            self.errmsg = "Verify guest pass printout failed: %s" % e.message
            
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
             
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
            
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf ={}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.passmsg = ''
        self.errmsg = ''
        
    def _retrieve_carribag(self):
        self.guest_pass = self.carrierbag['single_gp']['guest_pass']
        self.gprint_cfg = self.carrierbag['gprint_cfg']
        
        printout_name = self.gprint_cfg['name']
        printout_checker1 = self.gprint_cfg['gprint1_new'] % self.gprint_cfg['gprint1_needed']
        printout_checker2 = self.gprint_cfg['gprint2_new'] % self.gprint_cfg['gprint2_needed']
        self.printout_cfg = {'printout_name': printout_name,
                             'printout_checker1': printout_checker1,
                             'printout_checker2': printout_checker2
                             }

    def _update_carribag(self):
        pass
