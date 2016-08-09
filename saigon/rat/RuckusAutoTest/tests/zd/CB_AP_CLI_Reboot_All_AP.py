'''
Description:
    Reboot all AP which existed in testbed, and make sure all AP reboot DONE.
Create on 2013-8-15
@author: cwang@ruckuswireless.com
'''

import logging
import threading

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector


class CB_AP_CLI_Reboot_All_AP(Test):
    required_components = ['RuckusAP']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.aps = self.testbed.components['AP'] 
        self.active_ap_list = []    
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Try to reboot AP from AP CLI')
        if self.conf.has_key('ap_tag'):
            ap_tag = self.conf['ap_tag']
            if type(ap_tag) != list:
                ap_tag_list = [ap_tag]
            for aptag in ap_tag_list:
                self.active_ap_list.append(self.carrierbag[aptag]['ap_ins'])
        else:
            self.active_ap_list = self.aps
        try:
            _ll = []
            for ap in self.active_ap_list:
                if self.conf.has_key('force_ssh') and self.conf['force_ssh']:
                    _ll.append(threading.Thread(target=ap.reboot, kwargs = {'exit_on_pingable':True}))
                else:
                    _ll.append(threading.Thread(target=ap.reboot))
                
            for ins in _ll:
                ins.start()
            
            for ins in _ll:
                ins.join()
                
                
            logging.info('Reboot DONE.')        
        except Exception, e:
            import traceback
            logging.error(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
                        
        return self.returnResult('PASS', 'All AP reboot DONE.')
    
    def cleanup(self):
        self._update_carribag()