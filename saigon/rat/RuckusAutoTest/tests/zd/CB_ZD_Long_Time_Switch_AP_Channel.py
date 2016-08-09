# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
switch channel setting in ap config page continuously 
"""

import logging
import copy
import time

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import access_points_zd
from RuckusAutoTest.components.lib.apcli import radiogroup
from RuckusAutoTest.common import lib_List


class CB_ZD_Long_Time_Switch_AP_Channel(Test):
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
        
    def test(self):
        call_time = 1
        t0_set  =time.time()
        t0_check=time.time()
        while True:
            if time.time() - t0_set>=self.test_period_lenth:
                logging.info('has test for %s seconds'%self.test_period_lenth)
                break
            channel_idx_list,deploy_channel_list = self._get_channel_parameter(call_time)
            logging.info('set channel range time %s'%call_time)
            self._set_channel_range_in_ap_page(channel_idx_list)
            
            logging.info('wait %s seconds for ZD deploying the setting to ap...'%self.switch_interval)
            time.sleep(self.switch_interval)
            
            if time.time() - t0_check>=self.check_deploy_interval:
                logging.info('check ap channel deployment after %s time switch'%call_time)
                if not self._verify_channel_deploy_to_ap(deploy_channel_list):
                    self.errmsg = 'channel list deploy error after %s time switch'%call_time
                    break
                t0_check = time.time()
                    
            call_time+=1
        
        if self.errmsg:
            return 'FAIL',self.errmsg
            
        return ["PASS", self.passmsg]
    
    def cleanup(self):
        access_points_zd.disable_channel_selection_related_group_override(self.zd,self.ap_mac)

    def _cfg_init_test_params(self, conf):
        self.conf={'ng_channel_list':[],
                   'na_channel_list':[],
                   'test_period_lenth':0,
                   'switch_interval':0,
                   'check_deploy_interval':0,
                   'ap_mac':'',
                   'radio':'ng',
                   'ap_tag':'',#@author:yuyanan @since:2014-8-12 zf-9537
                   }
        self.conf.update(conf)
        
        self.ng_channel_list        = self.conf['ng_channel_list']
        self.na_channel_list        = self.conf['na_channel_list']
        self.test_period_lenth      = self.conf['test_period_lenth']
        self.switch_interval        = self.conf['switch_interval']
        self.check_deploy_interval  = self.conf['check_deploy_interval']
        
        if self.conf.get('ap_tag'):#@author:yuyanan @since:2014-8-12 optimize get ap mac from ap tag
            self.ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['ap_tag'])
        else:
            self.ap_mac = self.conf['ap_mac']
        self.ap     = self.testbed.mac_to_ap[self.ap_mac]
        self.radio  = self.conf['radio']
        
        if self.radio == 'na':
            self.channel_list = self.na_channel_list
        else:
            self.channel_list = self.ng_channel_list
            
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.passmsg = 'switch ap %s channel for %s hour finished'%(self.ap_mac,self.test_period_lenth)
        self.errmsg=''
 
    def _update_carrierbag(self):
        pass
    
    def _get_channel_parameter(self,call_time):
        channel_idx1 = [1,2]
        deploy_channel_list1 = [self.channel_list[0],self.channel_list[1]]
        
        channel_idx2 = [3,4]
        deploy_channel_list2 = [self.channel_list[2],self.channel_list[3]]
        
        if call_time%2:
            return channel_idx1,deploy_channel_list1
        else:
            return channel_idx2,deploy_channel_list2
    
    def _verify_channel_deploy_to_ap(self,channel_list):  
        logging.info('ap channel range should be %s'%channel_list)
        return self._verify_channel_setting_in_ap(self.ap,self.radio,channel_list) 

    def _verify_channel_setting_in_ap(self,ap,radio,channel_list):
        if radio=='bg' or radio=='ng':
            wifi_if='wifi0'
        else:    
            wifi_if='wifi1'
        return radiogroup.verify_available_channel_list(ap,channel_list,wifi_if)
    
    def _set_channel_range_in_ap_page(self,enable_channel_index_list):
        logging.info('set ap channel idx range to %s'%enable_channel_index_list)
        access_points_zd.set_channel_range(self.zd, self.ap_mac, True, self.radio, enable_channel_index_list)

    