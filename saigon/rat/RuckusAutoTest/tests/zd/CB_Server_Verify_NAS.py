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
        
        
Create on 2012-2-20
@author: cwang@ruckuswireless.com
'''

import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers

class CB_Server_Verify_NAS(Test):
    required_components = ['LinuxServer', 'ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(server_ip_addr = '192.168.0.252',
                         nas_identifier = "chris"
                         )
        self.conf.update(conf)        
        self.server_ip_addr = self.conf['server_ip_addr']
        self.sniffer = self.testbed.components['LinuxServer']
        self.zd = self.testbed.components['ZoneDirector']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Validate NAS-ID type attribute')
        cmd = ' radius.req'
        logging.info(cmd)   
        res = self.sniffer.read_tshark(cmd, return_as_list = False)
        total_req_cnt = len(re.findall("Code: Accounting-Request", res, re.M))
        if total_req_cnt == 0:
            return self.returnResult('FAIL', "No accounting request found.")
        
        cmd = ' radius.NAS_Identifier == "%s"' % self.conf.get('nas_identifier')
        logging.info(cmd)
        res = self.sniffer.read_tshark(cmd, return_as_list = False)
        total_id_cnt = len(re.findall("Code: Accounting-Request", res, re.M))
        if total_id_cnt < total_req_cnt:
            return self.returnResult('FAIL', 'NAS_Identifier lost.')
        
        return self.returnResult('PASS', 'NAS ID Type check pass.')
        
    def cleanup(self):
        self._update_carribag()