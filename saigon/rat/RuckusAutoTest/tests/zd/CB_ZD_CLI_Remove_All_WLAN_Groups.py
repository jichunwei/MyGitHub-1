'''
Created on 2011-1-20
@author: serena.tan@ruckuswireless.com

Description: This script is used to remove all wlan groups from ZD CLI.

'''


import logging
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers

class CB_ZD_CLI_Remove_All_WLAN_Groups(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._removeAllWLANGroups()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''

    def _removeAllWLANGroups(self):
        logging.info('Remove all WLAN groups from ZD CLI')
        try:
            ap_mac_list = self.testbed.get_aps_mac_list()
            logging.info("Default WLAN Groups for All APs")
            Helpers.zdcli.aps.default_wlan_groups_by_mac_addr(self.zdcli, ap_mac_list)
            logging.info("Default AP Group for All APs")
            Helpers.zdcli.aps.default_ap_group_by_mac_addr(self.zdcli, ap_mac_list)
            logging.info("Remove all wlan groups from the WLAN Groups table")        
            (res, msg ) = Helpers.zdcli.wgs.remove_all_wlan_groups(self.zdcli)
            if res:
                self.passmsg = msg            
            else:
                self.errmsg = msg
            
        except Exception, ex:
            logging.debug(traceback.format_exc())
            self.errmsg = ex.message        