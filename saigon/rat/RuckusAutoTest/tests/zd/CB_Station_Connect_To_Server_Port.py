'''
Created on Jun 19, 2014

@author: chen.tao@odc-ruckuswirelesss.com
'''

import logging
import time
from RuckusAutoTest.models import Test

class CB_Station_Connect_To_Server_Port(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',  
                         server_ip = '192.168.0.252',
                         port = '80',   
                         negative = False,                    
                         )
        self.conf.update(conf)
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
        server_ip = self.conf['server_ip']
        port = self.conf['port']
        logging.info("Trying to test if station could connect to %s on port %s"%(server_ip,port))
        res = self.target_station.connect_to_server_port(server_ip, port)
        if 'successful' in res:
            if self.conf['negative']:
                return self.returnResult('FAIL', 'Station could connect to %s on port %s'%(server_ip,port))
            else:
                return self.returnResult('PASS', 'Station could connect to %s on port %s'%(server_ip,port))
        else:
            if self.conf['negative']:
                return self.returnResult('PASS', res)
            else:
                return self.returnResult('FAIL', res)
    def cleanup(self):
        self._update_carribag()