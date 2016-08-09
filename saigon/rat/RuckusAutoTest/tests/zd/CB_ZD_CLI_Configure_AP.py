'''
Created on 2011-2-17
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure AP in ZD CLI.

'''
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_ap
import libZD_TestConfig as tconfig


class CB_ZD_CLI_Configure_AP(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._configureAP()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        self._updateCarrierbag()
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ap_cfg': {},
                     'ap_tag': '',
                     'update_time': 60}
        self.conf.update(conf)
        
        self.ap_cfg = self.conf['ap_cfg']

        if not self.ap_cfg and self.carrierbag.has_key('zdcli_ap_cfg'):
            self.ap_cfg = self.carrierbag['zdcli_ap_cfg']
            
        if self.conf['ap_tag']:
            active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['ap_tag'])
            self.ap_cfg.update({'mac_addr': active_ap.base_mac_addr})
            
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
    def _configureAP(self):
        try:
            res, msg = configure_ap.configure_ap(self.zdcli, self.ap_cfg)
            time.sleep(self.conf['update_time'])
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message
        
    def _updateCarrierbag(self):
        self.carrierbag['zdcli_ap_cfg'] = self.ap_cfg
        