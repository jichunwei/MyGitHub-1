'''
Description:
Linux server start to ping station and save the ping results to a file

Created on 2012-12-10
@author: zoe.huang@ruckuswireless.com

'''

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import create_server_by_ip_addr

class CB_ZD_Linux_Server_Ping_Station(Test):
    
    required_components = ['LinuxServer']
    parameter_description = {'sta_tag': 'station instance' }
      
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()   

    def test(self):        
        self._linux_server_ping_station()        
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', 'Linux server starts ping the wifi address of station successfully.')

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'sta_tag': 'STA1',
                     }
        self.conf.update(conf)       
        self.linuxserver = self.testbed.components['LinuxServer']            
        self.filename = '' #file to save ping results     
        self.serverlist = {}
        self.errmsg = ''
        
    def _retrive_carrier_bag(self):
        self.sta_wifi_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']           
    
    def _update_carrier_bag(self):
        self.carrierbag['file_save_ping_result'] = self.filename
        self.carrierbag['linux_server_instance'] = self.serverlist

    def _linux_server_ping_station(self):
        try:          
            if self.sta_wifi_addr is None or self.sta_wifi_addr == '':
                self.errmsg += 'There is no wifi address parameter passed'
                return
            linux_server = self._create_linux_server()
            self.filename = 'pingResult%s' % self.sta_wifi_addr
            linux_server.start_ping_station_wifi_addr(self.filename,self.sta_wifi_addr)
            logging.info('Linux server starts to ping wifi addr %s of station and save the results to file %s' % (self.sta_wifi_addr,self.filename))
            self.serverlist['LinuxServer'] = linux_server              
        except Exception, ex:
            self.errmsg = self.errmsg + ex.message
            
    def _create_linux_server(self): 
        linux_server = create_server_by_ip_addr(self.linuxserver.conf['ip_addr'],self.linuxserver.conf['user'],self.linuxserver.conf['password'],self.linuxserver.conf['root_password'])
        return linux_server
        
                      