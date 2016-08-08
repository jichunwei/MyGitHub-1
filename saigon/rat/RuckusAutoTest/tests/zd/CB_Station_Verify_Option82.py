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
from RuckusAutoTest.models import Test


class CB_Station_Verify_Option82(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',
                         src_ip_addr = '192.168.0.252'                         
                         )
        self.conf.update(conf)
        self.src_ip_addr = self.conf['src_ip_addr']
        self._retrieve_carribag()        
        self.errmsg = ""
        self.passmsg = ""
        
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):        
        (code, msg) = eval(self.target_station.analyze_tshark_traffic(params = " bootp.type == 0x02 and ip.src == %s" \
                                                                 % self.src_ip_addr, 
                                                                 expr="\(53")) #@author: Jane.Guo @since: 2013-10 adapt to windows7
        if code != 1:
            return self.returnResult("FAIL", "Haven't found any bootp ack/offer message")
        
        (code, msg) = eval(self.target_station.analyze_tshark_traffic(params = " bootp.type == 0x02 and ip.src == %s" \
                                                                 % self.src_ip_addr, 
                                                                 expr="\(82")) #@author: Jane.Guo @since: 2013-10 adapt to windows7
        if code == 1:
            return self.returnResult("FAIL", "bootp ack/offer messages contain dhcp option 82.")
        
        return self.returnResult('PASS', "Correct Behavior %s" % msg)
    
    def cleanup(self):
        self._update_carribag()