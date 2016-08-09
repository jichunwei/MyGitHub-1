# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to verify station exists on test bed
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import time
import logging
import libZD_TestConfig as tconfig 
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_Find_Station(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):
        self._findTargetStation()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag['station'] = self.target_station
        
        if self.carrierbag.has_key('station_list'):
            self.carrierbag['station_list'].append(self.target_station)
        else:
            self.carrierbag['station_list'] = []
            self.carrierbag['station_list'].append(self.target_station)
        msg = 'Config Station [%s] Successfully' % self.conf['target_station']
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.check_status_timeout=120
        self.conf = conf.copy()

    def _findTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                     , self.testbed.components['Station']
                                                     , check_status_timeout=self.check_status_timeout
                                                     , remove_all_wlan=True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])
