'''
Created on 2011-2-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to get AP's information from ZD GUI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import access_points_zd
import libZD_TestConfig as tconfig

class CB_ZD_Get_AP_Cfg(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._getAP()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        if conf.has_key('ap_tag') and conf['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, conf['ap_tag'])
            self.ap_mac_addr = active_ap.base_mac_addr
        else:
            self.ap_mac_addr = conf['ap_mac_addr']        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _getAP(self):
        try:
            self.ap_info = access_points_zd.get_ap_cfg_2(self.zd, self.ap_mac_addr)
            if not self.ap_info:
                self.errmsg = "Fail to get the configuration of AP [%s] from ZD GUI" % self.ap_mac_addr
            
            else:
                self.passmsg = "Get the configuration of AP [%s] from ZD GUI successfully" % self.ap_mac_addr
                
        except Exception, ex:
            self.errmsg = ex.message
            
    def _updateCarrierbag(self):
        self.carrierbag['zdgui_ap_info'] = self.ap_info
            
