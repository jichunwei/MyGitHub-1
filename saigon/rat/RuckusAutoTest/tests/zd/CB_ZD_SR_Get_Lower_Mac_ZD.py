import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd as red

class CB_ZD_SR_Get_Lower_Mac_ZD(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self.lower_mac_zd = self._get_lower_mac_zd()
        if self.zd1==self.lower_mac_zd:
            self.higher_mac_zd = self.zd2
            self.higher_mac_zdcli=self.zdcli2
            self.lower_mac_zdcli=self.zdcli1
        else:
            self.higher_mac_zd = self.zd1
            self.higher_mac_zdcli=self.zdcli1
            self.lower_mac_zdcli=self.zdcli2
        msg = "ZD [%s] with MAC address [%s] is Lower" % (self.lower_mac_zd.ip_addr,self.low_mac_address)
        self._update_carrier_bag()
        if self.errmsg:
            return 'FAIL',self.errmsg
        else:
            return 'PASS',msg
        

    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self._retrive_carrier_bag()


    def _get_lower_mac_zd(self):
#        self.zd1.navigate_to(self.zd1.ADMIN, self.zd1.ADMIN_PREFERENCE)
        mac_address1 = self.zd1.mac_addr
#        self.zd2.navigate_to(self.zd2.ADMIN, self.zd2.ADMIN_PREFERENCE)
        mac_address2 = self.zd2.mac_addr
        if cmp(mac_address1,mac_address2) == 1:
            self.low_mac_address = mac_address2
            self.high_mac_address = mac_address1
            return self.zd2
        else:
            self.low_mac_address = mac_address1
            self.high_mac_address = mac_address2
            return self.zd1
        
    def _retrive_carrier_bag(self):
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.zdcli1 = self.carrierbag['zdcli1']
        self.zdcli2 = self.carrierbag['zdcli2']

    
    def _update_carrier_bag(self):
        self.carrierbag['lower_mac_zd'] = self.lower_mac_zd
        self.carrierbag['higher_mac_zd'] = self.higher_mac_zd
        self.carrierbag['lower_mac_zdcli'] = self.lower_mac_zdcli
        self.carrierbag['higher_mac_zdcli'] = self.higher_mac_zdcli
        self.carrierbag['lower_mac_zd_mac'] = self.low_mac_address
        self.carrierbag['higher_mac_zd_mac'] = self.high_mac_address
        if self.carrierbag.has_key('active_zd'):
            if self.carrierbag['active_zd']==self.lower_mac_zd:
                self.carrierbag['active_zd_mac']=self.low_mac_address
                self.carrierbag['standby_zd_mac']=self.high_mac_address
            else:
                self.carrierbag['active_zd_mac']=self.low_mac_address
                self.carrierbag['standby_zd_mac']=self.high_mac_address
        
        
        

    
