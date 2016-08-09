'''
@author: serena.tan@ruckuswireless.com

Description: This script is used to verify if the station could associate with WLANs and ping target IP.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Associate_Test(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._associateStationWithWlans()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = dict(wlan_cfg_list = [],
                         target_station = "",
                         target_ip = '192.168.0.252',
                         check_status_timeout = 90,
                         ping_timeout = 60
                         )
        self.conf.update(conf)
        
        if self.conf['target_station']:
            self.target_station = self.carrierbag['station_list'][self.conf['target_station']]

        else:
            self.target_station = self.carrierbag['station']

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ""
        self.passmsg = ""
 
    def _associateStationWithWlans(self):
        try:
            for wlan_cfg in self.conf['wlan_cfg_list']:
                logging.info("Remove all WLANs from target station")
                tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])

                tmethod.assoc_station_with_ssid(self.target_station, wlan_cfg, self.conf['check_status_timeout'])
                
                tmethod.client_ping_dest_is_allowed(self.target_station,
                                                    self.conf['target_ip'],
                                                    ping_timeout_ms = self.conf['ping_timeout'] * 1000)
                       
            ssid_list = [wlan_cfg['ssid'] for wlan_cfg in self.conf['wlan_cfg_list']]
            self.passmsg = "Client associate with wlan %s and ping target IP [%s] successfully" % (ssid_list, self.conf['target_ip'])
            
            logging.info("Remove all WLANs from target station after test")
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])
        
        except Exception, ex:
            self.errmsg = ex.message

