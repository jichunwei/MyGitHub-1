'''
Created on Oct 31, 2013
@author: cwang@ruckuswireless.com
'''

import logging
import time
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import station_info_cli as StaGetter

class CB_CLI_Check_Clients(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):        
        self.conf = {'clientnum':0}
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']                        
        logging.info("====Initialize Params DONE====")
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):           
        res, msg = self._check_status(self.conf.get('clientnum'))
        return self.returnResult(res, msg)
    
    def cleanup(self):
        self._update_carribag()

    def _check_status(self, count = 0):
        timeout = 240
        s_t = time.time()
        flag = False
        msg = ''
        clients_data = []
        while time.time() - s_t < timeout:
            if count == 0:
                time.sleep(10)
            else:
                time.sleep(3)
                
            clients_data = StaGetter.show_all_current_active_clients(self.zdcli)
            if not clients_data and count !=0:
                logging.warning('Not any clients found, re-check.')
                time.sleep(3)
                
            elif clients_data and count == 0:
                return ('PASS', 'Not any client found.')
            
            (res, msg) = StaGetter.check_clients_status(clients_data)
            logging.info(msg)
            if res:                
                if len(clients_data) != count:
                    time.sleep(10)
                    continue                
                else:
                    return ('PASS', 'Correct Number')
                
        return ('FAIL', "clients number unmatches.")