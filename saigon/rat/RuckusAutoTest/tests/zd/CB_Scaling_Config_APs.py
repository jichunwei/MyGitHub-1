'''
Created on 2010-6-12
@author: cwang@ruckuswireless.com
'''
import logging
import random
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd as ap_helper

class CB_Scaling_Config_APs(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        
        if not self.aps_list:
            self.aps_list = self.testbed.get_aps_sym_dict()
            
        self.aps_list = self.aps_list.values()  
        self.aps_cfg_list = []
#        import pdb
#        pdb.set_trace()                
        for ap in self.aps_list:
            ap_cfg = ap_helper.get_ap_cfg_info(self.zd, ap['mac'])
            ap_cfg['mac'] = ap['mac']            
            logging.info('Store AP[%s] configuration[%s]' % (ap['mac'], ap_cfg))
            logging.info('Set AP[%s] configuration as [%s]' % (ap['mac'], self.conf))
#            self.conf['mac'] = ap['mac']
            description = self._geneate_string(64)
            ap_cfg['description'] = description
            ap_cfg['descrption'] = description
#            self.conf['description'] = description
            device_name = self._geneate_string(64)
            ap_cfg['device_name'] = device_name
            ap_cfg['device_location'] = self.conf['device_location']          
#            self.conf['device_name'] = device_name
            ap_cfg['gps_coordinates'] = self.conf['gps_coordinates']            
            ap_helper.set_ap_cfg_info(self.zd, ap_cfg)
	    time.sleep(.5)
            self.aps_cfg_list.append(ap_cfg)
            
        passmsg.append('AP configuration setting finished')           
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existing_aps_list'):
            self.aps_list = self.carrierbag['existing_aps_list']
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_aps_cfg_list'] = self.aps_cfg_list 
    
    def _init_test_params(self, conf):
        self.conf = dict(description = self._geneate_string(64), 
                         device_name = self._geneate_string(64),
                         device_location = self._geneate_string(64),
                         gps_coordinates = dict(latitude = '37.38813989', longitude = '-122.02586330'),
                         )
        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.aps_list = None
        self.errmsg = ''
        self.passmsg = ''
    
    def _geneate_string(self, size = 64):
        char_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''        
        random.seed()
        while size>0:
            lgt = len(char_string)
            index = random.randrange(0, lgt)
            result += char_string[index]
            size = size - 1
        return result
        
    
