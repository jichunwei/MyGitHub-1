import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Config_Wlan_Group_On_AP1(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):
        self._assignWlanGroupOnAP()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        msg = 'Config WlanGroup [%s] to AP [%s] on ZD Successfully' % (self.wgs_cfg['name'], self.active_ap.get_base_mac())
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        self.wgs_cfg = self.carrierbag['wgs_cfg'].copy()
        if self.conf.has_key('ap_rp'):
            self.wgs_cfg['ap_rp'].update(self.conf['ap_rp'])
        self.active_ap = self.carrierbag['active_ap']['AP1']
         
    def _assignWlanGroupOnAP(self):
        self.errmsg = zhlp.ap.cfg_wlan_groups_by_mac_addr( self.zd,
                                                         self.active_ap.get_base_mac(),
                                                         self.wgs_cfg['ap_rp'],
                                                         self.wgs_cfg['description'])
