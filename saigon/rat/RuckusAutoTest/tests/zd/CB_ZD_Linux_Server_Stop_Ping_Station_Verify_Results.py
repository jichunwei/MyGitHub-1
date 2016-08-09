'''
Description:
Linux server stops ping station and verify the results. 
If there is no 'Destination Host Unreachable', it means station never disconnects with the wlan.

Created on 2012-12-10
@author: zoe.huang@ruckuswireless.com

'''

import logging
import time
from RuckusAutoTest.models import Test

class CB_ZD_Linux_Server_Stop_Ping_Station_Verify_Results(Test):
    
    required_components = ['LinuxServer']
    parameter_description = {}
      
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()   

    def test(self):        
        self._linux_server_stop_ping_station()                     
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', 'Linux server stops ping the wifi address of station and verifies result successfully')

    def cleanup(self):
        if self.linux_server_case:
            self.linux_server_case.close()  

    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)       
        self.linuxserver = self.testbed.components['LinuxServer']            
        self.errmsg = ''
        
    def _retrive_carrier_bag(self):
        self.serverlist = self.carrierbag['linux_server_instance']
        self.linux_server_case =  self.serverlist['LinuxServer']
        self.filename = self.carrierbag['file_save_ping_result']           
    
    def _linux_server_stop_ping_station(self):
        try:
            logging.info('Stop ping the wifi addr of station')
            self.linux_server_case.close()
            pingResult = self.linuxserver.read_ping_station_results(self.filename)
            if 'Destination Host Unreachable' in pingResult:
                self.errmsg += 'Ping Results include Destination Host Unreachable. ERROR!'
        except Exception, ex:
            self.errmsg = self.errmsg + ex.message      
                      