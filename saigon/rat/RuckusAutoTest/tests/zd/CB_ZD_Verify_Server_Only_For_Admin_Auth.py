# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""

by west
verify some kind of server can only for admin authentication and authorization
for example tacacs pluss server 

"""

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.aaa_servers_zd import verify_server_only_for_admin_auth

class CB_ZD_Verify_Server_Only_For_Admin_Auth(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_parameter(conf)

    def test(self):
        self.errmsg = verify_server_only_for_admin_auth(self.zd,self.sever_list)
        if self.errmsg:
            return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_parameter(self, conf):
        self.conf = {'server_list':''
                    }
        self.conf.update(conf)
        self.sever_list=self.conf['server_list']
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''

    def _update_carrierbag(self):
        pass
