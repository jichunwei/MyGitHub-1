'''
Created on Jun 19, 2014

@author: chen.tao@odc-ruckuswirelesss.com
'''

import logging
import time
from RuckusAutoTest.models import Test


class CB_Station_Start_Iperf(Test):
    
    def _init_params(self, conf):
        self.conf = {'sta_tag':'',
                     'server_addr':'',
                     'test_udp': True,
                     'packet_len':'',
                     'bw':'',
                     'timeout':60,
                     'tos':'',
                     'multicast_srv':False,
                     'port':0               
                     }
        self.conf.update(conf)
        self.sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']      
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:    
            #logging.info(self.params)        
            self.sta.start_iperf(
                     self.conf['server_addr'],
                     self.conf['test_udp'],
                     self.conf['packet_len'],
                     self.conf['bw'],
                     self.conf['timeout'],
                     self.conf['tos'],
                     self.conf['multicast_srv'],
                     self.conf['port'])
            if self.conf['timeout']:
                logging.info("Sleep %s seconds while station sends traffic"%self.conf['timeout'])
                time.sleep(int(self.conf['timeout']))
        except Exception, ex:
            return self.returnResult('FAIL', ex.message)
        
        return self.returnResult('PASS', 'Station stars iperf successfully!')
    
    def cleanup(self):
        self._update_carribag()