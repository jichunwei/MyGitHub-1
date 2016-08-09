'''
Created on 2011-1-20
@author: serena.tan@ruckuswireless.com

Description: This script is used to configure WLAN groups in ZD CLI.

'''


from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups as cwg


class CB_ZD_CLI_Configure_WLAN_Groups(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._configureWLANGroups()
        
        if self.errmsg:
            if self.conf.get('negative'):
                return  self.returnResult('PASS', self.errmsg)
            else:
                return self.returnResult('FAIL', self.errmsg)
        else:
            if self.conf.get('negative'):
                return  self.returnResult('FAIL', self.passmsg)
            else:
                return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf={'negative':False}
        self.conf.update(conf)
        self.wg_cfg_list = self.conf['wg_cfg_list']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        self.errmsg = ''
        self.passmsg = ''

    def _configureWLANGroups(self):
        try:
            res, msg = cwg.configure_wlan_groups(self.zdcli, self.wg_cfg_list)
            if res:
                self.passmsg = msg
            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            self.errmsg = ex.message