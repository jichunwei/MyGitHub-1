# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:
remove specified wlan out of wlan group 

"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups

class CB_ZDCLI_Remove_Wlan_Out_Of_Wlan_Group(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        configure_wlan_groups.remove_wlan_members_from_wlan_group(self.zdcli, self.wlan_group_name, self.wlan_name_list)
        
        return ('PASS', 'remove wlans from wlan group successfully')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {
                     'wlan_name_list': [],
                     'wlan_group_name':''
                    }
        self.conf.update(conf)
        self.wlan_name_list = self.conf['wlan_name_list']
        self.wlan_group_name = self.conf['wlan_group_name']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]

        self.errmsg = ''
