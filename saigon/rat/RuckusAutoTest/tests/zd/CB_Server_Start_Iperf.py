'''
Created on Jun 19, 2014

@author: chen.tao@odc-ruckuswirelesss.com
'''

import logging
import time
from RuckusAutoTest.models import Test


class CB_Server_Start_Iperf(Test):
    
    def _init_params(self, conf):
        self.conf = {'server_addr':'',
                     'test_udp': True,
                     'packet_len':'',
                     'bw':'',
                     'timeout':'',
                     'tos':'',
                     'multicast_srv':False,
                     'port':0               
                     }
        self.conf.update(conf)
        self.server = self.testbed.components['LinuxServer']       
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:         
            self.server.start_iperf(
                     self.conf['server_addr'],
                     self.conf['test_udp'],
                     self.conf['packet_len'],
                     self.conf['bw'],
                     self.conf['timeout'],
                     self.conf['tos'],
                     self.conf['multicast_srv'],
                     self.conf['port'])
            logging.info("Sleep 5 seconds")
            time.sleep(5)
        except Exception, ex:
            return self.returnResult('FAIL', ex.message)
        
        return self.returnResult('PASS', '')
    
    def cleanup(self):
        self._update_carribag()