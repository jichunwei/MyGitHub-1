# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""
This script is used to create a single L2 ACL with one rule-to allow or deny a specific mac address.
Input: L2 acl config, the sta_tag or the mac address of the station, which you want to allow or deny.
Output: Result PASS(the acl is created),or FAIL(the acl could not be created).

Author: chen.tao@odc-ruckuswireless.com
Since:2013-05-13
"""


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_control_zd as AC


class CB_ZD_Create_L2_ACL_by_Mac_List(Test):
        
    def config(self, conf):        
        self._initTestParameters(conf)
            
    def test(self):
        try:
            AC.create_l2_acl_policy(self.zd,self.conf)
            return ("PASS", "L2_ACL %s is created successfully." % self.conf['acl_name'])
        except:
            return ("FAIL", "L2_ACL %s is not created." % self.conf['acl_name'])
                           
    def oncleanup(self):
        pass
    
    def _initTestParameters(self, conf):
        self.conf =  {'acl_name':'l2_acl_for_test',
                      'description':'',
                      'allowed_access':False,
                      'mac_list':[],
                      'sta_tag':''
                      }
        
        self.conf.update(conf)
        
        if self.conf['sta_tag']:
	        target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
	        target_station_mac = target_station.get_wifi_addresses()[1]
	        self.conf['mac_list'].append(target_station_mac)
        
        if 'active_zd' in self.carrierbag:
            self.zd = self.carrierbag['active_zd']
        else:
            self.zd = self.testbed.components['ZoneDirector']
                 
        self.errmsg = ''
        self.passmsg = ''


    
