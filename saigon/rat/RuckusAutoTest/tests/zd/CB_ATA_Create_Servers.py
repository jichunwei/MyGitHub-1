'''
Usage: createserver name [options]
Sample: createserver test1 
Created on Oct 15, 2013
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test

class CB_ATA_Create_Servers(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(servers = [])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.servers = self.conf.get('servers')
        logging.info('===========Initialize Params DONE ============')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        for server in self.servers:            
            rc = self.ata.create_server(**server)            
            time.sleep(2)
            logging.info('%s created' % server)
        
        res, msg = self.check_servers()
        
        if res:
            return self.returnResult('PASS', msg)
        else:
            return self.returnResult("FAIL", msg)
    
    def cleanup(self):
        self._update_carribag()
    
    
    def check_servers(self):
        """
        {'IPAddress': '192.168.0.159',
         'IPv4ConnectionState': 'DHCP Done',
         'IPv6ConnectionState': 'Global DAD Done',
         'L2ConnectionState': 'EAPOL Done',
         'MACAddress': '00:00:2f:7d:fb:44',
         'connectionState': 'ready',
         'port': 'enet_01',
         'serverName': 'server_01',
         'serverStats': {'ReceivedPingRequests': '1',
                         'SuccessfulARPHandshakes': '0',
                         'SuccessfulDHCPHandshakes': '1',
                         'TransmittedPingResponses': '0'},
         'serverStatus': 'ok_connected'}
        """
        timeout = 120
        st = time.time()        
        while time.time() - st < timeout:
            fnd = False
            for server in self.servers:
                svrname = server['servername']
                rc = self.ata.get_server_info(svrname)
                try:
                    if rc.has_key("IPAddress"):
                        if rc.get('connectionState', None) != "ready":
                            fnd = True
                            break
                                                
                    else:
                        fnd = True
                        break
                    
                except Exception, e:
                    logging.warning(e.message)            
            
            if fnd:
                time.sleep(3)
            else:
                return True, "all Servers are ready."
            
        
        return False, "Servers are not ready."