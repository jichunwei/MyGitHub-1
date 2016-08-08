"""
Description: This script is support to configure wlan group on AP by radio
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Config_Wlan_Group_On_AP(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._assign_wlan_group_on_ap()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        msg = 'Configure wlan group [%s] to AP [%s] on ZD successfully' % (self.wgs_cfg['name'], self.active_ap.get_base_mac())
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.wgs_cfg = self.conf['wgs_cfg'] if self.conf.has_key('wgs_cfg') else self.carrierbag['wgs_cfg']
        if self.conf.has_key('ap_rp'):
            self.wgs_cfg['ap_rp'].update(self.conf['ap_rp'])
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
         
    def _assign_wlan_group_on_ap(self):
        self.errmsg = zhlp.ap.cfg_wlan_groups_by_mac_addr( self.zd,
                                                         self.active_ap.get_base_mac(),
                                                         self.wgs_cfg['ap_rp'],
                                                         self.wgs_cfg['description'])
