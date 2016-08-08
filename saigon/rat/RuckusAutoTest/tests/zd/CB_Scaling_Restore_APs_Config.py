'''
Description:Resstore APs configurations to original setting.
Created on 2010-6-13
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.components.lib.zd import access_points_zd as ap_helper
from RuckusAutoTest.models import Test

class CB_Scaling_Restore_APs_Config(Test):
    '''
    Restore AP's configuration to previous cfg.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []

#Ignore aps_list info, just restore setting from aps_cfg_list, which came from CB_Scaling_Config_APs.py
#        if not self.aps_list:
#           self.aps_list = self.testbed.get_aps_sym_dict()
            
#       self.aps_list = self.aps_list.values()
#        if self.aps_cfg_list:
#            self.conf = self.aps_cfg_list[0]

	for ap_cfg in self.aps_cfg_list:
	    logging.info('Restore AP [%s] setting to orignal setting' % ap_cfg['mac'])
	    ap_helper.set_ap_cfg_info(self.zd, ap_cfg)
            
        passmsg.append('Restore APs setting successfully')
        self._update_carrier_bag()
        
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
#Ignore aps_list getting.	    
#        if self.carrierbag.has_key('existing_aps_list'):
#            self.aps_list = self.carrierbag['existing_aps_list']
            
        if self.carrierbag.has_key('existed_aps_cfg_list'):
            self.aps_cfg_list = self.carrierbag['existed_aps_cfg_list'] 
    
    def _update_carrier_bag(self):
        pass 
    
    def _init_test_params(self, conf):
        self.conf = dict(description = '', 
                         device_name = '',
                         device_location = '',
                         gps_coordinates = dict(latitude = '', longitude = ''),
                         )
        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _search_cfg_by_mac(self, mac_addr):
        for ap in self.aps_list:
            if ap['mac'] == mac_addr:
                return ap
            
        return None
    
