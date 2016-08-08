'''
Created on Oct 15, 2013

@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test


class CB_ATA_Create_Clients(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(clients=[])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.clients = self.conf.get('clients')        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         self.carrierbag['existed_clients'] = self.clients
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        cnt = 0
        for client in self.clients:
            self.ata.create_client(**client)
            logging.info("Create Client %s DONE" % client)
            cnt += 1
            time.sleep(cnt if cnt < 3 else  3)
        
        st = time.time()
        gpass = True
        msg = "Unknown"
        logging.info('Try to check clients during 120 seconds.')
        
        while time.time() - st < 120:
            res = False
            try:
                res, msg = self.verify_clients()
            except Exception, e:
                import traceback
                logging.error(traceback.format_exc())
                
            if not res:
                gpass = False
                logging.info(msg)
                time.sleep(2)
            else:
                gpass = True
                break                    
        
        if gpass:         
            return self.returnResult('PASS', msg)
        else:
            return self.returnResult('FAIL', msg)
    
    def cleanup(self):
        self._update_carribag()
        
    
    def verify_clients(self):
        for client in self.clients:
            clientname = client.get('clientname')
            clientinfo = self.ata.get_client_info(clientname, True)
            
            if clientinfo and not clientinfo.has_key("IPAddress"):
                return False, clientinfo
            elif not clientinfo:
                return False, "Not found."
            
            logging.info("Make sure client %s get valid IP address" % clientname)
            if clientinfo['IPAddress'] and clientinfo['IPAddress'].startswith("192.168"):
                if clientinfo['clientStatus'] == 'ok_connected':
                    client['IPAddress'] = clientinfo['IPAddress']                    
                else:
                    return False, "client: %s status: %s" % (clientinfo.get('clientname'), clientinfo.get('clientStatus'))
            else:
                return False, "client: %s,  ipaddr: %s" % (clientinfo.get('clientname'), clientinfo.get('IPAddress'))
        
        return True, "All clients are connected, and get IP address successfully."
            
        
            