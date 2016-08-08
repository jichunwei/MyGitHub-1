"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: 11-2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
        - 'ap_tag': 'active_ap'
        - 'type': 'rssi or default'

   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set the data to AP and check the result      
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If data are same between get and set 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import systemgroup


class CB_AP_CLI_Set_Mesh_Uplink_Selection(Test):
    required_components = ['RuckusAP']
    parameters_description = {'ap_tag': 'active_ap',
                              'type': 'rssi or default'}

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self._set_mesh_uplink_selection(self.type)
                
        except Exception, ex:
            self.errmsg = 'Set mesh uplink selection fail:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:
            self._update_carrier_bag()
            pass_msg = 'set AP mesh uplink selection method success'
            return self.returnResult('PASS', pass_msg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'ap_tag': 'AP_01', 'type': 'default'}
        self.conf.update(conf)
        self.type = self.conf['type']
        self.errmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
    
    def _update_carrier_bag(self):
        pass
     
    def _set_mesh_uplink_selection(self, type):
        logging.info("Set mesh uplink selection to %s" % type)
        result = systemgroup.set_mesh_uplink_selection(self.active_ap, type)
        if result:
            self.errmsg = result                    
