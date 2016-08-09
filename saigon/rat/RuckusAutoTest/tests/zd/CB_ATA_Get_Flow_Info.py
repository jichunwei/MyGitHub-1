'''
Created on Nov 11, 2013
@author: cwang@ruckuswireless.com
'''
import logging
import time
from RuckusAutoTest.models import Test

class CB_ATA_Get_Flow_Info(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(flowname = None)
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.flowname = self.conf.get('flowname')        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        """
        {'flowStats': {'status': 'Ready', 'AverageRXRate': '0.0', 'RXFlowIPOctets': '0', 'AverageTXRate': '100.0', 
        'FrameSize': '1000', 'RXFlowSumLatency': '0', 'RXFlowAvgLatency': '0', 'TXFlowIPOctets': '15992852', 
        'iRate': '100.0', 'RXFlowIPPackets': '0', 'connectionState': 'ARP Done', 'RXFlowLatencyCount': '0', 
        'RXFlowPacketsLost': '16286', 'TXFlowIPPackets': '16286'}, 'flowName': 'flow1', 'flowStatus': 'OK', 
        'target': '192.168.0.230', 'source': 'svr'}
        """
        timeout = 20
        st = time.time()
        while time.time() - st < timeout:
            res = self.ata.get_flow_info(flowname = self.flowname)
            if res.has_key("flowStats"):
                self.carrierbag['existed_%s' % self.flowname] = res['flowStats']
                return self.returnResult('PASS', 'get Flow %s successfully.' % self.flowname)
            else:
                time.sleep(2)
        
        return self.returnResult('FAIL', "Haven't find flow information about %s" % self.flowname)
        
    
    def cleanup(self):
        self._update_carribag()
        