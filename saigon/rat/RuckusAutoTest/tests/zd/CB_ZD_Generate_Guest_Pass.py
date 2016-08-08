# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
       
Create on 2011-07-11
@author: jluh@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga


class CB_ZD_Generate_Guest_Pass(Test):
    '''
    create the guestaccess policy on zd
    '''
    def config(self, conf):
        self._init_test_params(conf)
        
        
    def test(self):
        logging.info("Generate a Guest Pass on the ZD")
        self._generate_guest_pass_info()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = "Generate the guestpass successufully."
        logging.info(self.passmsg)
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)

               
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        if conf.has_key('use_static_key') and conf['use_static_key']:
            self.key = utils.make_random_string(16, type = "alnum")
        else:
            self.key = ""
        
        self.generate_guestpass_cfg = {'type':'single',
                                       'guest_fullname':'',
                                       'duration':'',
                                       'duration_unit': '',
                                       'wlan': '',
                                       'remarks': '',
                                       'key': self.key,
                                       'is_shared': 'No',
                                       'auth_ser': 'Local Database',
                                       'username': '',
                                       'password': '',}
        
        self.generate_guestpass_cfg.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _update_carrier_bag(self):
        if self.generate_guestpass_cfg['type'] == 'single':
            self.carrierbag['guest_pass'] = self.guest_pass_info['single_gp']['guest_pass']
            self.carrierbag['gp_expired_time'] = self.guest_pass_info['single_gp']['expired_time']
            self.carrierbag['guest_fullname'] = self.guest_pass_info['single_gp']['guest_name']
            self.carrierbag['single_gp'] = self.guest_pass_info['single_gp']

        else:
            pass  # stay on this step for the further page.
        
    
    def _generate_guest_pass_info(self):
        try:
            ga.generate_guestpass(self.zd, **self.generate_guestpass_cfg)
            self.guest_pass_info = ga.guestpass_info
            if not self.guest_pass_info:
                self.errmsg = "The generated Guest Pass is null."
                logging.debug(self.errmsg)
                raise Exception(self.errmsg)
        except Exception, ex:
            self.errmsg = '[Guest Pass generating failed] %s' % ex.message
            logging.debug(self.errmsg)
    

