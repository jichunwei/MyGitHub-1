'''
    Check XML attribute if existed.
     
Create on 2013-9-30
@author: cwang@ruckuswireless.com
'''

import logging
from copy import deepcopy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

class CB_Statistic_Attribute_Check(Test):
    required_components = []
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(attr=[])
        self.conf.update(conf)
        self.attr = self.conf.get("attr")
        self.attr = sorted(self.attr)
        
        
    def _retrieve_carribag(self):
        self.xml_dict_cfg = self.carrierbag['existed_xml_data_cfg']
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info("Begin check attribute of xml %s" % self.attr)
        invalidkeys=[]
        for item in self.attr:
            oitem=deepcopy(item)
            item.reverse()            
            cfg = self.xml_dict_cfg        
            
            for i in range(len(item)):
                tag = item.pop()
                if not cfg.has_key(tag):
                    invalidkeys.append((oitem, "Not found %s" % tag))
                    break
                
                cfg = cfg[tag]
                
        if invalidkeys:
            self.returnResult("FAIL", str(invalidkeys))
        
                
        return self.returnResult('PASS', 'All of attribute existed.')
    
    
    def cleanup(self):
        self._update_carribag()
        