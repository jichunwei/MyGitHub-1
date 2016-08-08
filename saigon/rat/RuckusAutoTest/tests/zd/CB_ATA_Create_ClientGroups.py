'''
Create Client Groups from ATA.
    Usage: createClientGroup groupName count ssid [options]
    Sample: createClientGroup g2 10 chris-open-none
    
Check Client Groups from ATA.
    Usage: getClientGroupInfo groupName [options]
    Sample: getClientGroupInfo g2
      
Created on Oct 15, 2013
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test


class CB_ATA_Create_ClientGroups(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(clientgroups=[])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.clientgroups = self.conf['clientgroups']        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        
    def test(self):
        cnt = 0
        for cgrp in self.clientgroups:
            if not cgrp.has_key('group_name'):
                continue
            if not cgrp.has_key('count'):
                continue
            if not cgrp.has_key("ssid"):
                continue
            
            self.ata.create_client_group(**cgrp)
            logging.info("Create Client group %s DONE" % cgrp['group_name'])
            cnt += 1            
            time.sleep(cnt * int(cgrp['count']))
        
        if cnt:            
            return self.returnResult('PASS', '%d clientgroup(s) be created' % cnt)
        else:
            return self.returnResult('FAIL', 'Not any clientgroup be created, please check your configuration.')    
    
    def cleanup(self):
        self._update_carribag()