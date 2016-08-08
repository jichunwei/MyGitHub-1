# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
 
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.components.lib.zd import access_points_zd as AP
from RuckusAutoTest.components.lib.apcli import shellmode as ap_shell

class CB_ZD_Set_AP_Channel(Test):
    def config(self, conf):
        self.conf={'ap_index':0,
                   'radio':'2.4',
                   'channel':'1'}
        self.conf.update(conf)
        self.zd=self.testbed.components['ZoneDirector']
        self.ap_mac_list=self.testbed.get_aps_mac_list()
        self.ap_mac=self.ap_mac_list[self.conf['ap_index']]
        self.radio=self.conf['radio']
        self.channel=self.conf['channel']
        self.errmsg=''
        self.passmsg=''
        
    def test(self):
        AP.set_ap_channel(self.zd, self.ap_mac, self.radio, self.channel)
        self.carrierbag['active_ap']=self.testbed.mac_to_ap[self.ap_mac.lower()]
        if self.errmsg:
            return('FAIL',self.errmsg)
        return('PASS','ap channel set in zd web UI works correctly')

    def cleanup(self):
        pass

        