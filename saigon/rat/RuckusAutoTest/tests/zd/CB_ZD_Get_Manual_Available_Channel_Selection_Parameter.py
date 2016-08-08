# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
form the carribag get test parameter for one round test
by west
"""

import logging

from RuckusAutoTest.models import Test

class CB_ZD_Get_Manual_Available_Channel_Selection_Parameter(Test):
    def config(self, conf):
        '''
        self.para_key_list=['single_band_ap_test_para','dule_band_ap_test_para','outdoor_ap_test_para',
                            'US_dfs_channel_test_para','dfs_channel_test_para','cband_channel_test_para',
                            'uk_cband_channel_test_para','precedency_para','backup_para']
        '''
        self.conf={'para_key':'single_band_ap_test_para'}
        self.conf.update(conf)
        self.passmsg = 'get test parameter for %s successfully'%self.conf['para_key']
        

    def test(self):
        
        self._update_carrier_bag()     
        logging.info(self.passmsg)
        #set outdoor ap test parameter       
        return ["PASS", self.passmsg]

    def cleanup(self):
        pass
    
        
    def _update_carrier_bag(self):
        self.carrierbag['channel_selection_test_para']=self.carrierbag['test_para'][self.conf['para_key']]
        if 'US_dfs_channel_test_para'==self.conf['para_key']:
            self.carrierbag['channel_optimization'] = self.carrierbag['channel_selection_test_para']['channel_optimization']
        if self.conf['para_key'] in ['US_dfs_channel_test_para','dfs_channel_test_para','cband_channel_test_para','uk_cband_channel_test_para',]:
            self.carrierbag['allow_indoor_channel'] = self.carrierbag['channel_selection_test_para']['allow_indoor_channel']
        

