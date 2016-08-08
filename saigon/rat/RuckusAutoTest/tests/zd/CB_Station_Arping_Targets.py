'''
Description:
    Ping target list as:
        ['ip': 'mac',
         '192.168.0.233', 'aa:aa:aa:aa:aa:aa']
         
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
        
@author: An Nguyen, an.nguyen@ruckuswireless.com
@since: Jun 2012
'''

import logging

from RuckusAutoTest.models import Test

class CB_Station_Arping_Targets(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carrierbag()
    
    def test(self):
        self._verify_arping()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)                             
    
    def cleanup(self):
        self._update_carrierbag()
        
    def _init_params(self, conf):
        self.conf = {'allow': True, #ping allow(True|False) in target list.
                     'sta_tag': 'sta_1',
                     'dest_sta_tag': '',
                     'target_list': [],
                     }
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''        
    
    def _retrieve_carrierbag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        if self.conf['dest_sta_tag']:
            wifi_ip = self.carrierbag[self.conf['dest_sta_tag']].get('wifi_ip_addr')
            wifi_mac = self.carrierbag[self.conf['dest_sta_tag']].get('wifi_mac_addr')
            if not wifi_ip or not wifi_mac:
                raise Exception('There is not any wifi address info of station %s in carrier bag' % self.conf['dest_sta_tag'])
            self.conf['target_list'].append((wifi_ip, wifi_mac))
            
    def _update_carrierbag(self):
        pass
    
    def _verify_arping(self):
        """
        """
        for ip, mac in self.conf['target_list']:
            logging.info('Try to broadcast the arp packet to %s:' % ip)
            arpres = self.target_station.send_arping(**{'dest_ip': ip})       
            res = arpres.get(ip) == mac
        
            if res != self.conf['allow']:
                msg = ' allowed but not return the expected MAC' if self.conf['allow'] else ' successfully but not allowed'
                self.errmsg += ' [ARPing %s] %s.' % (ip, msg)
            else: 
                msg = ' allowed and return the correct MAC' if self.conf['allow'] else ' failed as expected'
                self.passmsg = '[ARPing %s] %s' % (ip, msg)