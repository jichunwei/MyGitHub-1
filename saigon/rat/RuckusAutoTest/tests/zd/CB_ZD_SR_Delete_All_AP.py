
import logging
from copy import deepcopy
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components.lib.zd import redundancy_zd as red


class CB_ZD_SR_Delete_All_AP(Test):
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        zd1_state = red.get_local_device_state(self.zd1)
        zd2_state = red.get_local_device_state(self.zd2)
        
        if self.conf.has_key('zd'):
            self.zd = self.carrierbag[self.conf.get('zd')]
            self.zd._delete_all_aps()
            if self.errmsg:
                return ('FAIL', self.errmsg)
            msg = 'Delete %s all AP successfully ' % self.zd.get_ip_cfg()
            return('PASS', msg)
        
        if zd1_state == "active":
            self.zd1._delete_all_aps()
        elif zd2_state == "active":
            self.zd2._delete_all_aps()
        else:
            self.zd1._delete_all_aps()
            self.zd2._delete_all_aps()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        msg = 'Delete all AP successfully '
        return ('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = conf
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
   

    