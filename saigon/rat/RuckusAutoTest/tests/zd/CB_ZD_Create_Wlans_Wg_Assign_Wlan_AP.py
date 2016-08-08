# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Aug 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters:
        - ap_tag: 'ap tag',
        - radio_mode: 'radio mode',
        - wlan_cfg_list: 'wlan configure list',
        - enable_wlan_on_default_wlan_group: 'whether enable wlan on default wlan group',
        - wgs_cfg: 'wlan group configuration'
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Create wlans or edit exist ones
        - Remove wlan from default wlan group is enable_wlan_on_default_wlan_group is false
        - Create empty wlan group or edit exist one. 
        - Assign wlans to the wlan group   
        - Assign AP to wlan group for specified radio mode
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If wlan and wlan created, wlans are assigned to wlan group, and ap is assigned to wlan group successfully 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class CB_ZD_Create_Wlans_Wg_Assign_Wlan_AP(Test):
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {'ap_tag': 'ap tag',
                             'radio_mode': 'radio mode',
                             'wlan_cfg_list': 'wlan configure list',
                             'enable_wlan_on_default_wlan_group': 'whether enable wlan on default wlan group',
                             'wgs_cfg': 'wlan group configuration',
                             'deploy_wlan_timeout': ' Timeout for deploy wlan configuration to AP.',
                             'check_wlan_timeout': 'Waiting for some time after create a wlan.'}

    def config(self, conf):
        default_wgs_cfg = dict(ap_rp={'bg':{'wlangroups':'WLAN_GROUP_1'}},
                               name='WLAN_GROUP_1',
                               description='WLAN_GROUP_1')
        
        self.conf = dict(deploy_wlan_timeout = 40,
                         check_wlan_timeout = 4,
                         wlan_cfg_list = [],
                         enable_wlan_on_default_wlan_group=False,
                         wgs_cfg=default_wgs_cfg,                         
                         )
        self.conf.update(conf)
                
        self.wlan_cfg_list = self.conf['wlan_cfg_list']
        self.wg_cfg = self.conf['wgs_cfg']
                
        wlan_name_list = []
        for wlan_cfg in self.wlan_cfg_list:
            wlan_name_list.append(wlan_cfg['ssid'])
        self.wlan_name_list = wlan_name_list
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.radio_mode = self.conf['radio_mode']
        
        self.errmsg = ""
        self.passmsg = ""
        self.zd = self.testbed.components['ZoneDirector']

    def test(self):
        logging.info('Create new wlans or edit exist ones')
        current_wlanlist = lib.zd.wlan.get_wlan_list(self.zd)
        if current_wlanlist == None: current_wlanlist = []
        for wlan_cfg in self.wlan_cfg_list:
            if wlan_cfg['ssid'] in current_wlanlist:
                self._cfg_edit_wlan_on_zd(wlan_cfg)
            else:
                self._cfg_create_wlan_on_zd(wlan_cfg)  
                
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self.carrierbag['wlan_cfg_list'] = self.wlan_cfg_list
        
        if self.conf['enable_wlan_on_default_wlan_group'] == False:
            logging.info('Remove the wlans from default wlan group')
            for wlan_cfg in self.wlan_cfg_list:
                self._rm_wlan_from_default_wlangroup(wlan_cfg)
            
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
            
        logging.info('Create a new wlan group or edit a exist one')        
        if lib.zd.wgs.find_wlan_group(self.zd, self.wg_cfg['name']):
            self._cfg_edit_wlan_group_on_zd()
        else:
            self._cfg_create_empty_wlan_group_on_zd()
            
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        self.carrierbag['wgs_cfg'] = self.wg_cfg
        
        logging.info('Assign wlans to wlan group')
        self._cfg_assign_wlan_to_wlangroup()
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        
        logging.info('Assign AP to wlan group')
        ap_wgs_cfg = {}
        ap_wgs_cfg.update(self.wg_cfg)
        ap_wgs_cfg['description'] = None
        ap_wgs_cfg['ap_rp'] = {self.radio_mode: {'wlangroups': self.wg_cfg['name']}}
        self._assign_wlan_group_on_ap(ap_wgs_cfg)
        
        logging.info('Waiting %s for ZD to push config to the APs' % (self.conf['deploy_wlan_timeout']))
        tmethod8.pause_test_for(self.conf['deploy_wlan_timeout'], 'Wait for ZD to push config to the APs')
        
        if self.errmsg: return self.returnResult("FAIL", self.errmsg)
            
        self.passmsg = "Create wlans %s, wlan group %s and assign wlan to wlan group, AP to wlan group successfully" \
                         % (self.wlan_name_list, self.wg_cfg['name'])
        return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        pass

    def _cfg_edit_wlan_on_zd(self, wlan_cfg):
        logging.info("Edit WLAN [%s] with new setting on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, wlan_cfg['ssid'], wlan_cfg)
        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _cfg_create_wlan_on_zd(self, wlan_cfg):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, wlan_cfg)
        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _rm_wlan_from_default_wlangroup(self, wlan_cfg):
        self.errmsg = lib.zd.wgs.uncheck_default_wlan_member( self.zd, wlan_cfg['ssid'])
        
    def _cfg_create_empty_wlan_group_on_zd(self):
        self.errmsg = lib.zd.wgs.create_wlan_group(self.zd, self.wg_cfg['name'], [], False, self.wg_cfg['description'])
        
    def _cfg_edit_wlan_group_on_zd(self):
        self.errmsg = lib.zd.wgs.edit_wlan_group(self.zd, self.wg_cfg['name'], self.wg_cfg['name'], self.wg_cfg['description'])
        
    def _cfg_assign_wlan_to_wlangroup(self):
        self.errmsg = lib.zd.wgs.cfg_wlan_group_members(self.zd, self.wg_cfg['name'], self.wlan_name_list, True)        
        
    def _assign_wlan_group_on_ap(self, wgs_cfg):
        self.errmsg = lib.zd.ap.cfg_wlan_groups_by_mac_addr( self.zd, self.active_ap.get_base_mac(), wgs_cfg['ap_rp'], wgs_cfg['description'])