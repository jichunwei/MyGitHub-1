"""
Description: This script is used to remove all wlans from the target station.
Author: Jacky Luh
Email: jluh@ruckuswireless.com
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_Station_Remove_All_Wlans(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testRemoveWlanFromStation()
        self._update_carrier_bag()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = 'Remove all wlans from target station successfully'

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_station_timeout': 120}
        self.conf.update(conf)
        if self.carrierbag.has_key('Station'):
            self.sta_tag_obj = self.carrierbag['Station'][self.conf['sta_tag']]['sta_ins']
        else:
            self.sta_tag_obj = self.carrierbag[self.conf['sta_tag']]['sta_ins']

        self.errmsg = ''
        self.passmsg = ''

    def _testRemoveWlanFromStation(self):
        try:
            #@author: Anzuo, release ip addr for dhcp service
            self.sta_tag_obj.do_release_wifi_ip_address()

            logging.info("Remove all wlans from the stations")
            tconfig.remove_all_wlan_from_station(self.sta_tag_obj, check_status_timeout=self.conf['check_station_timeout'])
        except Exception, e:
            self.errmsg = '[Removing wlan from target station failed] %s' % e.message
  
    def _update_carrier_bag(self):
        self.carrierbag[self.conf['sta_tag']] = dict()
        self.carrierbag[self.conf['sta_tag']]['sta_ins'] = self.sta_tag_obj 