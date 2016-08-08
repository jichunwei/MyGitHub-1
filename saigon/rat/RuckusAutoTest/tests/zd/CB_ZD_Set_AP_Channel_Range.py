# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
set ap channel range in ap config page
"""

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd

class CB_ZD_Set_AP_Channel_Range(Test):
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._set_channel_range_in_ap_page(self.conf['na_channel_idx_list'],self.conf['ng_channel_idx_list'])
        
        if self.errmsg:
            return 'FAIL',self.errmsg
            
        return ["PASS", self.passmsg]
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf={'ng_channel_idx_list':[],
                   'na_channel_idx_list':[],
                   'ap_mac':'',
                   'ap_tag':'',
                   }
        self.conf.update(conf)
        
        if self.conf['ap_tag']:
            self.ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['ap_tag'])
            if not self.ap_mac:
                self.errmsg = "Active AP[%s]'s mac not found in testbed." % self.conf['ap_tag']
                return
        else:
            self.ap_mac = self.conf['ap_mac']     
            
        self.zd = self.testbed.components['ZoneDirector']
        
        self.passmsg = 'set ap channel range successfully'
        self.errmsg=''
 
    def _update_carrierbag(self):
        pass
    
    def _set_channel_range_in_ap_page(self,enable_na_channel_index_list,enable_ng_channel_index_list):
        logging.info('set ap channel idx range to %s(na),%s(ng)'%(enable_na_channel_index_list,enable_ng_channel_index_list))
        access_points_zd.set_channel_range(self.zd, self.ap_mac, True, 'na', enable_na_channel_index_list)
        access_points_zd.set_channel_range(self.zd, self.ap_mac, True, 'ng', enable_ng_channel_index_list)

    