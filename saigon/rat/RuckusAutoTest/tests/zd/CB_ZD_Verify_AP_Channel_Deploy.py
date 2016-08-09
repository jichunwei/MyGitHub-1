# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
switch channel setting in ap config page continuously 
"""

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import radiogroup

class CB_ZD_Verify_AP_Channel_Deploy(Test):
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._verify_channel_deploy_to_ap()
        
        if self.errmsg:
            return 'FAIL',self.errmsg
            
        return ["PASS", self.passmsg]
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf={'ng_channel_list':[],
                   'na_channel_list':[],
                   'ap_mac':'',
                   'ap_tag':'',
                   }
        self.conf.update(conf)
        
        self.ng_channel_list        = self.conf['ng_channel_list']
        self.na_channel_list        = self.conf['na_channel_list']
        
        if self.conf['ap_tag']:
            self.ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['ap_tag'])
            if not self.ap_mac:
                self.errmsg = "Active AP[%s]'s mac not found in testbed." % self.conf['ap_tag']
                return
        else:
            self.ap_mac = self.conf['ap_mac']
               
        self.ap     = self.testbed.mac_to_ap[self.ap_mac]
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.passmsg = 'ap channel verify OK'
        self.errmsg=''
 
    def _update_carrierbag(self):
        pass
    
    def _verify_channel_deploy_to_ap(self):  
        logging.info('ap channel range should be %s(na),%s(ng)'%(self.na_channel_list,self.ng_channel_list))
        res_na= self._verify_channel_setting_in_ap(self.ap,'na',self.na_channel_list) 
        res_ng= self._verify_channel_setting_in_ap(self.ap,'ng',self.ng_channel_list) 
        msg=''
        if not res_na:
            msg += 'na channel not deploy correctly,'
        if not res_ng:
            msg += 'ng channel not deploy correctly,'
        if msg:   
            logging.error(msg)
            self.errmsg=msg
        

    def _verify_channel_setting_in_ap(self,ap,radio,channel_list):
        if radio=='bg' or radio=='ng':
            wifi_if='wifi0'
        else:    
            wifi_if='wifi1'
        return radiogroup.verify_available_channel_list(ap,channel_list,wifi_if)
    
    