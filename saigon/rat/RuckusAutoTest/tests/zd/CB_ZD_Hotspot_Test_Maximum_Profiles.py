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
        
        
Create on 2011-8-16
@author: cwang@ruckuswireless.com
'''

import logging
import time
from copy import deepcopy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Hotspot_Test_Maximum_Profiles(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(number_of_profile = 32,
                         hotspot_cfg = {'login_page': 'http://192.168.0.250/login.html',
                                        'name': 'maxinum_profiles_test'} ,
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        h_cfg_list = []
        for i in range(int(self.conf['number_of_profile'])):
            h_cfg = deepcopy(self.conf['hotspot_cfg'])
            h_cfg['name'] = '%s_%d' % (h_cfg['name'], i)
            h_cfg_list.append(h_cfg)
        
        self.conf['hotspot_cfg_list'] = h_cfg_list
        self.errmsg = ''
        self.msg = ''
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        
        try:
            logging.info("Try to create %s Hotspot profiles" %
                         self.conf['number_of_profile'])
            for cfg in self.conf['hotspot_cfg_list']:
                logging.info("Create a Hotspot profile [%s] on the "
                             "ZoneDirector" % cfg['name'])
                lib.zd.wispr.create_profile(self.zd, **cfg)
                time.sleep(3)
            self.msg += "%s Hotspot profiles have been created successfully. " \
                        % self.conf['number_of_profile']

        except:
            self.errmsg = "Unable to create %s Hotspot profiles" \
                          % self.conf['number_of_profile']

            return self.returnResult('FAIL', self.errmsg)

        try:
            logging.info("Try to create one more Hotspot profile")
            cfg = copy.deepcopy(self.conf['hotspot_cfg'])
            cfg['name'] = "%s-extra" % cfg['name']
            lib.zd.wispr.create_profile(self.zd, **cfg)
            self.errmsg = "The ZD did allow creating more than " \
                          "%s Hotspot profiles" % self.conf['number_of_profile']
            
            return self.returnResult('FAIL', self.errmsg)

        except:
            self.msg += "The ZD didn't allow creating more than "\
                        "%s Hotspot profiles. " % self.conf['number_of_profile']
            return self.returnResult('PASS', self.msg)                
        
    def cleanup(self):
        self._update_carribag()