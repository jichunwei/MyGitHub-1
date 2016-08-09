'''
Try ping to target IP from Active AP.
Created on 2011-4-26
@author: cwang@ruckuswireless
'''
from RuckusAutoTest.models import Test

class CB_AP_Ping(Test):
    '''
        Ping target AP from Active_AP
    '''
    required_components = ['RuckusAP']
    test_parameters = {'target_ip':'ip addr of zd',
                       'timeout_ms': 'time out'}
    
    def config(self, conf):
        self.conf = {'target_ip':'192.168.0.2',
                     'timeout_ms': 30 * 1000,
                     'ap_index':0}
        self.conf.update(conf)
        self._retrive_param_from_carribag()
    
    def test(self):
        res = self.active_ap['AP1'].ping_from_ap(self.conf['target_ip'], timeout_ms = self.conf['timeout_ms'])
        if res.startswith('Ping OK'):
            return self.returnResult('PASS', 'ping %s with time %s' % (self.conf['target_ip'], self.conf['timeout_ms']))
        else:
            return self.returnResult('FAIL', res)
    
    def cleanup(self):
        pass
    
    def _retrive_param_from_carribag(self):
        if 'active_ap' in self.carrierbag.keys():
            self.active_ap = self.carrierbag['active_ap']
        elif self.conf.has_key('ap_index'):
            self.ap_mac_list=self.testbed.get_aps_mac_list()
            self.ap_mac=self.ap_mac_list[self.conf['ap_index']]
            self.active_ap1=self.testbed.mac_to_ap[self.ap_mac.lower()]
            self.active_ap={}
            self.active_ap['AP1']=self.active_ap1
        else:
            raise Exception("Please define active ap fristly.")
        
        if self.carrierbag.has_key('stand_alone_ip'):
            self.conf['target_ip']=str(self.carrierbag['stand_alone_ip'])
            
