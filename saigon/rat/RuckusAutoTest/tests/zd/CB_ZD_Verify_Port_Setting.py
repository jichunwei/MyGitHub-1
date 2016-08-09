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
        
        
Create on 2012-3-19
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers


class CB_ZD_Verify_Port_Setting(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(port_setting = None)
        self.conf.update(conf)
        self.port_setting = self.conf['port_setting']
        self.zd = self.testbed.components['ZoneDirector']
    
    def _retrieve_carribag(self):
        self.port_setting_gui = self.carrierbag["existed_port_setting_gui"] 
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        (res, info) = self._verify_port_info()
        if res:
            return self.returnResult('PASS', 'Expect info equal Actual info.')
        else:
            return self.returnResult("FAIL", info)
    
    def cleanup(self):
        self._update_carribag()
        
        
    def _verify_port_info(self):
        _dd = {}        
        for key, value in self.port_setting_gui.items():
            if key in self.port_setting.keys():
                _dd[key] = value
                
        for key, value in _dd.items():
            for k2, v2 in self.port_setting.items():
                if k2 == key and v2 is str:
                    if v2 != value:
                        return (False, "Expect info %d, actual info %s" % \
                                (self.port_setting, self.port_setting_gui))
                elif k2 == key and v2 is dict:
                    if not self._verify_ap_info(v2, value):
                        return (False, "Expect info %d, actual info %s" % \
                                (self.port_setting, self.port_setting_gui))
        
        return (True, "")
                    
                
                
    def _verify_ap_info(self, expect_info, actual_info):
        cli_ks = expect_info.keys()
        gui_ks = actual_info.keys()
        
        for key in gui_ks:
            if key not in cli_ks:
                logging.info('The parameter [%s] of AP [%s] exists in GUI but not in CLI' % \
                             (key, actual_info['mac']))
                return False
            
            if expect_info[key] != actual_info[key]:
                logging.info("The information of AP [%s] in CLI [%s = %s] is not the same as in GUI [%s = %s]" % \
                             (expect_info['mac'], key, expect_info[key], key, actual_info[key]))
                return False
            
        logging.info('The information of AP [%s] in CLI is correct!' % expect_info['mac'])
        return True

        
            