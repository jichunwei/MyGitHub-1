'''
Created on 2011-4-21
@author: cwang@ruckuswireless.com
'''
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD

class CB_ZD_Assign_Wlan_To_Wlangroup(Test):
         
    def config(self, conf):
        self.conf = conf
        self.zd = self.testbed.components['ZoneDirector']
        self.wlan_name_list = self.conf['wlan_name_list']
        self.wlangroup_name = self.conf['wlangroup_name']
    def test(self):
        try:
            Helper_ZD.wgs.cfg_wlan_group_members(self.zd, self.wlangroup_name,
                                                self.wlan_name_list, check=True)
            time.sleep(40)#wait for configuration to be assigned
            return self.returnResult('PASS', 'WLANs%s have been assigned to wlangroup[%s]' \
                                     % (self.wlan_name_list, self.wlangroup_name))
        except Exception:
            import sys
            return self.returnResult('FAIL', sys.exc_info())
        
    def cleanup(self):
        pass