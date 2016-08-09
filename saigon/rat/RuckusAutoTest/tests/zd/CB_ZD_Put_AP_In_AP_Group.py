# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
set parameter used by Manual Available Channel Selection cases
put them in carrierbag
"""

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import access_points_zd


class CB_ZD_Put_AP_In_AP_Group(Test):
    def config(self, conf):
        self._retrive_carrierbag()
        self._cfg_init_test_params(conf)
        
        
    def test(self):
        for mac in self.ap_mac_list:
            logging.info('put ap %s in ap group %s'%(mac,self.ap_group_name))
            access_points_zd.set_ap_general_by_mac_addr(self.zd,mac,ap_group=self.ap_group_name)
        return self.returnResult('PASS', 'put aps %s in ap group %s successfully'%(self.ap_mac_list,self.ap_group_name))
    
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf={'ap_group_name':'',
                   'ap_mac_list':[]}
        self.conf.update(conf)
        self.ap_group_name = self.conf['ap_group_name']
        self.ap_mac_list   = self.conf['ap_mac_list']
        self.zd = self.testbed.components['ZoneDirector']
        
    
    def _retrive_carrierbag(self):
        pass
    
    def _update_carrierbag(self):
        pass
                                                    
    