# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to test spectralink phone with different encryption
Author: Jason Lin
Email: jlin@ruckuswireless.com

Test Parameters: {}
Result type:PASS/FAIL
Results:PASS:kill tshark daemon on station
        FAIL:
                  
Test Procedure:
1. config:
   - paser tshark_enable value from carrierbag
2. test:
   if carrierbag['tshark_enable'] = True:
       kill tshark daemon on station
   else:
       return "No tshark daemon running"
3. cleanup:
   - pass
"""
import logging
from RuckusAutoTest.models import Test

class CB_ZD_Stop_Sniffer_On_Station(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):
        self._stopCapturePktsOnStation()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        msg = 'Start Tshark to Sniffer Packets on Station [%s] Successfully' % self.target_station.sta_ip_addr
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = conf.copy()
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        if self.carrierbag.has_key('sniffer_enable'):
            self.sniffer_enable = self.carrierbag['sniffer_enable']
        
    def _stopCapturePktsOnStation(self):
        if self.sniffer_enable:
            self.carrierbag['sniffer_enable']=False
            return self.target_station.do_cmd('TA.killTshark')
        else:
            logging.info("No TShark Daemon running")
            self.errmsg = "No TShark Daemon runnig"