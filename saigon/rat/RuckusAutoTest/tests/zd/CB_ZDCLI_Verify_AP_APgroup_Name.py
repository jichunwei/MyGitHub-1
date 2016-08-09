"""
verify the aps in the specified ap group or not 
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.ap_info_cli import get_ap_group_name


class CB_ZDCLI_Verify_AP_APgroup_Name(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        
        for mac in self.ap_mac_list:
            apg_name = get_ap_group_name(self.zdcli,mac)
            if not apg_name==self.apg_name:
                self.errmsg+='ap %s in group %s,'%(mac,apg_name)
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ap_mac_list': [],
                     'apg_name':''}
        self.conf.update(conf)
        self.ap_mac_list = self.conf['ap_mac_list']
        self.apg_name = self.conf['apg_name']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        else:
            self.zdcli=self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = 'all aps in ap group [%s]'%self.apg_name
        
