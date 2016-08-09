# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
verify the in ap cli the channel deployment is correct
"""

import logging
import time
import copy

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.apcli import radiogroup
from RuckusAutoTest.common import lib_List


class CB_ZD_Verify_AP_Channel_Deployment_After_Restore(Test):
    def config(self, conf):
        self._retrive_carrierbag()
        self._cfg_init_test_params(conf)
        
    def test(self):
        if self.expect_same:
            if not self._verify_channel_setting_in_ap(self.ap,'ng',self.ng_channel_list):
                self.errmsg='ap %s ng channel setting can not deploy to ap after restore'%self.ap
                logging.error(self.errmsg)
            if not self._verify_channel_setting_in_ap(self.ap,'na',self.na_channel_list):
                self.errmsg='ap %s na channel setting can not deploy to ap after restore'%self.ap
                logging.error(self.errmsg)
        else:
            available_channel_ng=self._get_available_channel_in_ap(self.ap,'ng')
            available_channel_na=self._get_available_channel_in_ap(self.ap,'na')
            temp = [int(channel) for channel in available_channel_ng]
            available_channel_ng = copy.copy(temp)
            temp = [int(channel) for channel in available_channel_na]
            available_channel_na = temp
            logging.info('available_channel_ng %s'%available_channel_ng)
            logging.info('available_channel_na %s'%available_channel_na)
            logging.info('self.ng_channel_list %s'%self.ng_channel_list)
            logging.info('self.na_channel_list %s'%self.na_channel_list)
            res_ng = lib_List.list_in_list(self.ng_channel_list, available_channel_ng) and (len(available_channel_ng)>len(self.ng_channel_list))
            if not res_ng:
                self.errmsg='ap ng channel setting can not deploy to ap after restore,[%s] not in [%s]'%(self.ng_channel_list,available_channel_ng)
                logging.error(self.errmsg)
            res_na = lib_List.list_in_list(self.na_channel_list, available_channel_na) and (len(available_channel_na)>len(self.na_channel_list))
            if not res_na:
                self.errmsg='ap na channel setting can not deploy to ap after restore,[%s] not in [%s]'%(self.na_channel_list,available_channel_na)
                logging.error(self.errmsg)
        if self.errmsg:
            return 'FAIL',self.errmsg
        return ["PASS", self.passmsg]
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf={'restore_type':''}
        self.conf.update(conf)
        if self.conf['restore_type']=='restore_everything' or self.conf['restore_type']=='restore_everything_except_ip':
            self.expect_same=True
        else:
            self.expect_same=False
        
        self.passmsg = 'the channel is the same as expected'
        self.errmsg=''
        
    
    def _retrive_carrierbag(self):
        self.ap=self.carrierbag['backed_channel_info']['ap']
        self.ng_channel_list = self.carrierbag['backed_channel_info']['ng_channel_list']
        self.na_channel_list = self.carrierbag['backed_channel_info']['na_channel_list']
        
    def _verify_channel_setting_in_ap(self,ap,radio,channel_list):
        if radio=='bg' or radio=='ng':
            wifi_if='wifi0'
        else:    
            wifi_if='wifi1'
        return radiogroup.verify_available_channel_list(ap,channel_list,wifi_if)
    

    def _get_available_channel_in_ap(self,ap,radio):
        if radio=='bg' or radio=='ng':
            wifi_if='wifi0'
        else:    
            wifi_if='wifi1'
        return radiogroup.get_available_channel_list(ap,wifi_if)   
    