"""
Description: This script is support to configure wlan on wlan group
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class CB_ZD_Config_Wlan_On_Wlan_Group(Test):
    def config(self, conf):
        self._cfg_init_test_params(conf)
         
    def test(self):
        if self.conf.has_key('check_wlan_timeout'):
            timeout = int(self.conf['check_wlan_timeout'])
        else:
            timeout = 20
        self._config_wlan_on_wlan_group(timeout)
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Configure wlan[%s] on wlan group[%s] successfully' % \
                       (self.active_wlan_list, self.wgs_cfg['name'])
        return self.returnResult('PASS', self.passmsg)
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.wgs_cfg = self.conf['wgs_cfg'] if self.conf.has_key('wgs_cfg') else self.carrierbag['wgs_cfg']
        self.active_wlan_list = self.conf['wlan_list']
        
    def _config_wlan_on_wlan_group(self, timeout):
        self.errmsg = zhlp.wgs.cfg_wlan_group_members(self.zd, self.wgs_cfg['name'], self.active_wlan_list, True)
        tmethod8.pause_test_for(timeout, 'Wait for ZD to push config to the APs')
