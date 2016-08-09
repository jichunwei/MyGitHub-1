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
        
        
Create on 2012-3-28
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test


class CB_ZD_Create_WireStation(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_ip_addr='192.168.1.11',
                         sta_tag = 'sta_1',
                         )
        self.conf.update(conf)
        self.station_list = self.testbed.components['Station']
        
        self.errmsg = ''
        self.passmsg = ''        
        self.sta_tag = self.conf['sta_tag']
        self.sta_ip_addr = self.conf['sta_ip_addr']
        self.carrierbag[self.sta_tag]={}
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        for sta in self.station_list:
            if sta.get_ip_addr() == self.sta_ip_addr:        
                self.carrierbag[self.sta_tag]['sta_ins'] = sta
                passmsg = 'Create Station [%s %s] Successfully' % (self.sta_tag, self.sta_ip_addr)
                return self.returnResult('PASS', passmsg)
    
        return self.returnResult('FAIL', "Haven't found station {%s}" % self.sta_ip_addr)
    
    def cleanup(self):
        pass