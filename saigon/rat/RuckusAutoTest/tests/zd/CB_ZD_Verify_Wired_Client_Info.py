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
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_ZD_Verify_Wired_Client_Info(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'sta_tag':'sta_1',
                     'user':'',                     
                     'ap_mac_addr':'',
                     'lan_port': 'LAN2',
                     'status':'Unauthorized',                 
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.expect_info = {'mac':'',
                            'user': self.conf.get('user'),
                            'ap':self.conf.get('ap_mac_addr'),
                            'port_id':self.conf.get('lan_port'),
                            'status':self.conf.get('status'),
                            }
        
    def _retrieve_carribag(self):
        if self.carrierbag[self.conf['sta_tag']].has_key("wired_sta_ip_addr"):
            self.wired_sta_mac_addr = self.carrierbag[self.conf['sta_tag']]['wired_sta_mac_addr']
            self.wired_sta_ip_addr = self.carrierbag[self.conf['sta_tag']]['wired_sta_ip_addr']
            
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        self.expect_info['mac'] = self.wired_sta_mac_addr
        #@author: yin.wenling ZF-9940 2014-9-18
        if self.expect_info['user'] == self.conf['sta_tag']:
            self.expect_info['user'] =  self.wired_sta_mac_addr.lower()
      
    def test(self):   
        s_t = time.time()
        timeout = 300
        while time.time() - s_t < timeout:            
            self.zd.s.refresh() 
            try:        
                cinfo = Helpers.zd.awc.get_active_client_status_by_mac(self.zd, self.wired_sta_mac_addr)
                
                if cinfo == None or cinfo['status'] != self.expect_info['status']:                    
                    logging.info('Re-check because status is unmatched')
                    time.sleep(10)
                else:
                    if cinfo['status'] == 'Authorized' and self.expect_info['user']=='':
                        self.expect_info['user'] = self.wired_sta_ip_addr      
                    (res, message) = self._verify(cinfo)
                    if not res:
                        logging.warning(message)
                        time.sleep(3)
                    else:
                        return self.returnResult("PASS", "Check PASS.")
            except Exception, e:
                import traceback
                logging.warning(e.message)
                time.sleep(5)                
                
        
             
        return self.returnResult('FAIL', 
                                 "Expected: %s, Actual: %s" % (self.expect_info, cinfo))
        
#        if self.conf.get('status') == "Authorized":
#            message_type = "MSG_wire_client_join"#Wired {user} joins {port} from {ap}
#            pattern1 = self.zd.messages[message_type]
#            pattern1 = pattern1.replace('{user}', 'User[%s]' % self.conf['user'])
#            pattern1 = pattern1.replace('{port}', '%s' % self.conf['lan_port'])
#            pattern1 = pattern1.replace('{ap}', 'AP[%s]' % self.conf['ap_mac_addr'])
#            s_time = time.time()
#            while time.time() - s_time < 60:
#                events_log = self.zd.get_events()
#                logging.info(events_log)
#                
#                fnd = False
#                for event in events_log:
#                    if pattern1 in event:
#                        fnd = True
#                        break
#                
#                if fnd:
#                    break
#                else:
#                    time.sleep(5)
#                
#            if not fnd:
#                return self.returnResult("FAIL", "haven't found any event log %s" % pattern1)
                
    
    def _verify(self, cinfo):
        for key, value in cinfo.items():
            for k2, v2 in self.expect_info.items():
                if k2 == key:
                    if value != v2:
                        return (False, "Expected info %s, actual info %s" % (self.expect_info, cinfo))
        
        return (True, "All of information are matched.")
    
    
    def cleanup(self):
        pass