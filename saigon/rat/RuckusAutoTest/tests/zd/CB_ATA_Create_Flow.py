'''
Created on Nov 7, 2013
@author: lab
'''
import logging
import time
from RuckusAutoTest.models import Test

class CB_ATA_Create_Flow(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(clients=[])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.flowname = self.conf.get('flowname')
        self.servername = self.conf.get('servername')
        self.clientname = self.conf.get('clientname')
    
    def _retrieve_carribag(self):
        if self.carrierbag.has_key("existed_clients"):
             self.existed_clients = self.carrierbag['existed_clients']
        else:
             raise Exception("Can't find key 'existed_clients' in carrier bag.")
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        res = self.ata.create_flow(flowname = self.flowname, 
                                   source=self.servername,
                                   destin = self.get_ip_addr_by_client_name())
        
        res, msg = self.check_flow()
        logging.info(res)
        if res:
            return self.returnResult('PASS', msg)
        else:
            return self.returnResult('FAIL', msg)
    
    def cleanup(self):
        self._update_carribag()
        
    def get_ip_addr_by_client_name(self):        
        for client in self.existed_clients:
            if client.get('clientname') == self.clientname:
                return client['IPAddress']
        
        raise Exception("Haven't find any IP Address against client %s" % self.clientname)
    
    
    def check_flow(self):
        timeout = 20
        st = time.time()
        while time.time() - st < timeout:
            info = self.ata.get_flow_info(self.flowname)
            if info.has_key("flowStats"):
                return True, "Flow %s created successfully" % self.flowname
            
            else:
                time.sleep(1)
        
        
        return False, "Flow  %s doesn't created successfully" % self.flowname
