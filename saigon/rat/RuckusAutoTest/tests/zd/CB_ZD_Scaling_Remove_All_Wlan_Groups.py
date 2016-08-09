'''
Description:
Created on 2010-8-18
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging


from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Scaling_Remove_All_Wlan_Groups(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyRemoveAllWlanGroups()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.carrierbag['existing_wlan_groups'] = []

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyRemoveAllWlanGroups(self, ruckus_ap_list = []):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            logging.info("Remove all WLAN Groups on the Zone Director.")
            lib.zd.wgs.remove_wlan_groups(self.zd, ap_mac_addrList = ruckus_ap_list)
            self.passmsg = 'All WLAN Groups are deleted successfully'
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[WLAN Groups deleting failed] %s' % e.message
            logging.debug(self.errmsg)
    
