# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
clear test env for Manual Available Channel Selection cases
"""

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components.lib.zd import access_points_zd


class CB_ZD_Clear_Env_For_Manual_Available_Channel_Selection_test(Test):
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        ap_grp_num =ap_group.get_apg_total_number(self.zd)
        for ap_mac in self.ap_mac_list:
            if not ap_grp_num == 1:
                access_points_zd.set_ap_general_by_mac_addr(self.zd,ap_mac,ap_group='System Default')
            access_points_zd.disable_channel_selection_related_group_override(self.zd,ap_mac)
        if not ap_grp_num == 1:
            ap_group.delete_ap_group_by_name(self.zd,self.conf['ap_group'])
        ap_group.set_channelization(self.zd,'System Default','Auto')
        return ["PASS", self.passmsg]
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf={'ap_group':'',
                   'clear_all_ap':False}
        self.conf.update(conf)
        
#        self.apg=self.conf['ap_group']
        if self.carrierbag.has_key('backed_channel_info') and self.carrierbag['backed_channel_info']['ap'] and not self.conf['clear_all_ap']:
            if type(self.carrierbag['backed_channel_info']['ap']) is not list:
                self.ap_mac_list = [self.carrierbag['backed_channel_info']['ap'].base_mac_addr]
            else:
                self.ap_mac_list = [ap.base_mac_addr for ap in self.carrierbag['backed_channel_info']['ap']]
        elif self.conf.get('ap_tag_list'):
            self.ap_mac_list = []
            for ap_tag in self.conf['ap_tag_list']:
                ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(ap_tag)
                if not ap_mac:
                    self.errmsg = self.errmsg + "Active AP[%s]'s mac not found in testbed.\n" % ap_tag
                else:
                    self.ap_mac_list.append(ap_mac)
        elif self.conf.get('ap_mac_list'):
            self.ap_mac_list = self.conf['ap_mac_list']
        else:
            self.ap_mac_list = self.testbed.get_aps_mac_list()
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.get('zd'):
            self.zd = self.carrierbag[self.conf['zd']]
        self.passmsg = 'clear enviroment successfully'
        self.errmsg=''
        
    