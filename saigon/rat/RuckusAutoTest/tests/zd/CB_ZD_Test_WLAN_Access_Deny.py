'''
Created on 2011-3-22
@author: serena.tan@ruckuswireless.com

Description: This script is used to test the WLAN access deny.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Test_WLAN_Access_Deny(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testStationCanNotAssociateToWlan()
        if self.errmsg: 
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = dict(wlan_cfg = {},
                         sta_tag = '',
                         check_status_timeout = 90,
                         check_wlan_timeout = 3,
                         pause = 2.0,
                         )
        self.conf.update(conf)
        
        if self.conf['sta_tag']:
            self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
            
        elif self.conf.has_key("target_station"):
            self.target_station = self.carrierbag['station_list'][self.conf['target_station']]

        else:
            self.target_station = self.carrierbag['station']

        self.wlan_cfg = self.conf['wlan_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
            
    def _cfgGetTargetStation(self):
        logging.info("Find the target station on the test bed")
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                                       self.testbed.components['Station'],
                                                       check_status_timeout = self.conf['check_status_timeout'],
                                                       remove_all_wlan = True)
        if not self.target_station:
            self.errmsg = "Target station %s not found" % self.conf['target_station']
        
    def _RemoveWlanFromStation(self):
        logging.info("Remove all WLANs from the station")
        try:
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])
        
        except Exception, ex:
            self.errmsg = ex.message
            
    def _testStationCanNotAssociateToWlan(self):
        logging.info("Test the station can not associate to WLAN [%s]." % self.wlan_cfg['ssid'])
        try:
            self.res = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.conf['check_status_timeout'])
            if not self.res:
                self.errmsg = "Station can associate to WLAN [%s], wrong behavior" % self.wlan_cfg['ssid']
                return
            
            self.msg = tmethod.verify_wlan_in_the_air(self.target_station, self.wlan_cfg['ssid'])
            if "The station couldn't associate to the WLAN although the beacons of the WLAN were found on the air" in self.msg:
                self.passmsg = "Beacons of the WLAN [%s] was found on the air but the station couldn't associate to it, correct behavior" % self.wlan_cfg['ssid']
            
            else:
                self.errmsg = self.msg
            
        except Exception, ex:
            self.errmsg = ex.message
        
                