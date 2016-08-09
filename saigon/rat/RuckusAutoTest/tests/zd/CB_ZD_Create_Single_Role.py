"""
Description: 

by Louis
Create a single role on ZD

"""

import logging
#from copy import deepcopy

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components import Helpers as lib
#from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class CB_ZD_Create_Single_Role(Test):
#    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
#    parameter_description = {
#                          }

    def config(self, conf):
#        self.conf = dict(check_status_timeout = 90,
#                         check_wlan_timeout = 3,
#                         pause = 2.0,
##                         enable_wlan_on_default_wlan_group=True
#                         role_cfg = {"rolename": "", "rat-role": "", "guestpass": True, "description": "",
#                                         "group_attr": "", "zd_admin": ""}
#                            )

        self.conf = dict(role_cfg = {"rolename": "", "specify_wlan": "", "guestpass": True, "description": "",
                                     "group_attr": "", "zd_admin": ""}
        )

        self.conf.update(conf)
        self.errmsg = ""
        self.passmsg = ""
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        self.role_cfg = self.conf['role_cfg']

    def test(self):
        
        try:
            
            self.zd.create_role(**self.role_cfg)
            logging.info('role [%s] create successfully' % self.role_cfg['rolename'])
            self.passmsg = "role [%s] create successfully" % self.role_cfg['rolename']
        
        except Exception, e:
            
            self.errmsg = 'there is something wrong when create a role, detail %s' % e.message
        
        if self.errmsg:
            return("FAIL",self.errmsg)
        
        return ("PASS",self.passmsg)

    def cleanup(self):
        pass
