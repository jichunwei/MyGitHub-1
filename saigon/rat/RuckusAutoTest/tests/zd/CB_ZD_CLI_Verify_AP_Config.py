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
        
        
Create on 2012-11-14
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
import libZD_TestConfig as tconfig

class CB_ZD_CLI_Verify_AP_Config(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ap_cfg = None)
        self.conf.update(conf)
        self.ap_cfg = self.conf.get('ap_cfg', None)
        if self.ap_cfg['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.ap_cfg['ap_tag'])
            self.ap_cfg.update({'mac_addr': active_ap.base_mac_addr})
    
    def _retrieve_carribag(self):
        self.existed_ap_cfg = self.carrierbag.get('existed_ap_cfg', None)
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        res, msg = self.validate_radio_cfg()  
        if res:      
            return self.returnResult('PASS', msg)
        else:
            return self.returnResult('FAIL', msg)
    
    def cleanup(self):
        pass
#        self._update_carribag()
        
    
    def validate_radio_cfg(self):
        KEY_MAP = {'radio_na':"Radio a/n",
                   'radio_bg':"Radio b/g/n",
                   'radio_ng':"Radio b/g/n",
                   'radio_a': "Radio a",
                   }
        _cfg = {}
        for key in self.ap_cfg:
            if key in KEY_MAP:
                _cfg[KEY_MAP[key]] = self.ap_cfg[key]
        logging.info('Check radio configuration.')           
        return self._check_radio_cfg(_cfg, self.existed_ap_cfg)
    
    def _check_radio_cfg(self, expected_cfg, actual_cfg):
        for key, value in expected_cfg.items():
            if key in actual_cfg:
                a_cfg = actual_cfg.get(key)
                for k, v in value.items():
                    if k == "ac":
                        kk = "Call Admission Control"
                        if v+"%" not in a_cfg[kk]:
                            return (False, 
                                    "Expected: %s=%s, actual: %s=%s" % (k, v, k, a_cfg[kk]))
                    
                    else:
                        if v != a_cfg[k]:
                            return (False,
                                    "Expected: %s=%s, actual: %s=%s" % (k, v, k, a_cfg[k]))
                
        
        return (True, "Radio setting is equal.")