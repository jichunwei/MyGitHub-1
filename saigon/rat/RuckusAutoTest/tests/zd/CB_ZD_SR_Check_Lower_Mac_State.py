#import os
#import re
import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Check_Lower_Mac_State(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)

    def test(self):
        lower_mac_zd,higher_mac_zd = self._get_lower_mac_zd()
        lower_mac_zd_state = red.get_local_device_state(lower_mac_zd)
        
        if lower_mac_zd_state != self.conf['except_state']:
            self.errmsg = "The expect state is", self.conf['except_state'],"but the result is", lower_mac_zd_state
        
        self.carrierbag['lower_mac_zd']=lower_mac_zd
        self.carrierbag['higher_mac_zd']=higher_mac_zd
        
        if lower_mac_zd_state=='active':
            self.carrierbag['active_zd']=lower_mac_zd
            self.carrierbag['standby_zd']=higher_mac_zd
        else:
            self.carrierbag['active_zd']=higher_mac_zd
            self.carrierbag['standby_zd']=lower_mac_zd
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

            
        msg = 'The state of ZD with Lower MAC address is the excepted state:',self.conf['except_state']
        return self.returnResult('PASS', msg)


    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         except_state = 'active'
                         )

        self.conf.update(conf)

        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']

    def _get_lower_mac_zd(self):
        self.zd1.navigate_to(self.zd1.ADMIN, self.zd1.ADMIN_PREFERENCE)
        mac_address1 = self.zd1.mac_addr
        self.zd2.navigate_to(self.zd2.ADMIN, self.zd2.ADMIN_PREFERENCE)
        mac_address2 = self.zd2.mac_addr
        if cmp(mac_address1,mac_address2) == 1:
            logging.info("ZD [%s] with MAC address [%s] is Lower",self.zd2.ip_addr,mac_address2)
#            self.higher_mac_zd = self.zd1
#            self.carrierbag['higher_mac_zd'] = self.zd1
#            self.carrierbag['lower_mac_zd'] = self.zd2
            return self.zd2,self.zd1
        else:
            logging.info("ZD [%s] with MAC address [%s] is Lower",self.zd1.ip_addr,mac_address1)
#            self.higher_mac_zd = self.zd2
#            self.carrierbag['higher_mac_zd'] = self.zd1
#            self.carrierbag['lower_mac_zd'] = self.zd2
            return self.zd1,self.zd2

