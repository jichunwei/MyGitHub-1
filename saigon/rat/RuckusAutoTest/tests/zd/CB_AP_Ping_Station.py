'''
Try to ping target station wifi IP from active AP.
Created on 2012-12-11
@author: sean.chen@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

class CB_AP_Ping_Station(Test):
    
    required_components = ['RuckusAP']
    test_parameters = {'ap_tag': 'tag of active AP', 
                       'sta_tag': 'tag of station', 
                       'target_ip':' wifi IP addr of target station',
                       'timeout_ms': 'time out'}
    
    def config(self, conf):
        self.conf = {'ap_tag': 'ap1',
                     'sta_tag': 'sta1',
                     'target_ip':'192.168.0.1',
                     'timeout_ms': 10 * 1000}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.conf.update({'target_ip': self.sta_wifi_ip_addr})
        
        
    #@author:yuyanan @since:2014-8-20 optimize:add try_num hope ping success
    def test(self):
        #@ZJ ZF-9771
        res = self.active_ap.ping_from_ap(self.conf['target_ip'], timeout_ms = self.conf['timeout_ms'])
        if res.startswith('Ping OK'):
            return self.returnResult('FAIL', 'AP should not ping station: %s successfully when Proxy arp is enabled.' % self.conf['target_ip'])
        #@ZJ ZF-9771
        return self.returnResult('PASS', res)
    
    
    def cleanup(self):
        pass
    
    def _retrieve_carribag(self):
        if self.conf['ap_tag'] in self.carrierbag.keys():
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        else:
            raise Exception("Please define active ap fristly.")
        
        self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        