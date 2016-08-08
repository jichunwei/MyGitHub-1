"""
Description: This script is support to create a wlan on ZD
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Create_Single_Wlan(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._createWlan()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        if self.conf['disable_wlan_on_default_wlan_group'] == True:
            self._remove_wlan_on_default_wlan_group()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag[self.wlan_cfg['ssid']] = self.wlan_cfg
        msg = 'Create wlan [%s] with auth[%s] encryption[%s] on ZD successfully' % \
                  (self.wlan_cfg['ssid'], self.wlan_cfg['auth'], self.wlan_cfg['encryption'])
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf={'disable_wlan_on_default_wlan_group':True}
        self.conf.update(conf)
        self.errmsg = ''
        self.wlan_cfg={}
        if conf.has_key('wlan_cfg'):
            self.wlan_cfg.update(conf['wlan_cfg'])
        else:
            self.wlan_cfg = conf.copy()
        self.zd = self.testbed.components['ZoneDirector']
        
    def _createWlan(self):
        self.errmsg = zhlp.wlan.create_wlan(self.zd, self.wlan_cfg)
        
    def _remove_wlan_on_default_wlan_group(self):
        self.errmsg = zhlp.wgs.uncheck_default_wlan_member( self.zd, self.wlan_cfg['ssid'])

