
"""
Description: To verify if ZD could send radius accounting message to radius accounting server correctly
            Including Acct-Start, Acct-Interm-Update, Acct-Stop.  
"""

import os
import time
import logging
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import set_wlan as wlan

class CB_ZD_Modify_WLAN_Nas_Id_Type(Test):
    required_components = ['ZoneDirector', 'ZoneDirectorCLI']
    parameter_description = {}

#    test_cfgs.append(({'wlan_cfg': wlan_cfg,
#                       'acct_nas_id_type': new_nas_id_type,
#                       'user_define_string': user_def_str,

    def config(self, conf):
        self.conf   = conf.copy()
        self.zd     = self.testbed.components['ZoneDirector']
        self.zdcli  = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ""
        self.passmsg = ""

    def test(self):
        wlan_conf={'name':self.conf['wlan_cfg']['ssid'], 
                   'nas_id_type':self.conf['acct_nas_id_type'], 
                   'nas_id_value':self.conf.get('user_define_string')}

        try:
            wlan.set_nas_id_type(self.zdcli, wlan_conf)
        except Exception, e:
            return self.returnResult('FAIL', e.message)

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
