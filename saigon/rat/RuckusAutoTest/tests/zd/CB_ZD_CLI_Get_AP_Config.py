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

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as aphlp
import libZD_TestConfig as tconfig

class CB_ZD_CLI_Get_AP_Config(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ap_mac = None)
        self.conf.update(conf)
        
        if self.conf.has_key('ap_tag') and self.conf['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['ap_tag'])
            self.ap_mac = active_ap.base_mac_addr
        else:
            self.ap_mac = self.conf.get('ap_mac', None)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        self.carrierbag['existed_ap_cfg'] = self.ap_cfg
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self.ap_cfg = aphlp.show_ap_info_by_mac(self.zdcli, self.ap_mac)
        if self.ap_cfg:
            _cfg = self.ap_cfg['AP']['ID']
            self.ap_cfg = _cfg.values()[0]
            self._update_carribag()                  
            return self.returnResult('PASS', 'Get AP Configuration successfully')
        else:
            return self.returnResult('FAIL', "Haven't find AP %s" % self.ap_mac)
    
    def cleanup(self):
        pass
