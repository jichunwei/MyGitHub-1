"""
Description: This combo test is used perform multiple hop speedflex on AP
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - Zone Director
    - AP support speedflex
Input: 
    - N/A
Output: 
    - PASS: If speedflex run correctly  
    - FAIL: If speedflex could not start or result not qualify (speed rate and packets loss)
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from pprint import pformat
import libZD_TestConfig as tconfig
import logging, re

class CB_ZD_Speedflex_On_MultiHop_MeshAP(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)
        self._get_ap_mac_list()

    def test(self):
        result = self._test_multihop_speedflex()
        if self.errmsg: 
            return self.returnResult("FAIL", self.errmsg)
        return self.returnResult('PASS', result)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'timeout':5000,
                     'rate_limit': 0, 
                     'min_rate': 0.0,
                     'max_rate': 100.0, 
                     'accept_packets_loss': 5} # percentage
        self.conf.update(conf)
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap_list = self.conf['active_ap_list']
        self.ap_mac_list = []
        
        if self.conf['rate_limit']:
            self.conf['max_rate'] = self.conf['rate_limit']
        
    def _get_ap_mac_list(self):
        for ap in self.active_ap_list: 
            self.ap_mac_list.append(tconfig.get_testbed_active_ap(self.testbed, ap).get_base_mac())
        
    def _test_multihop_speedflex(self):
        result = lib.zd.sp.run_multihop_speedflex_performance(self.zd, self.ap_mac_list)
        logging.info("Speedflex Performance Result: %s" % pformat(result))
        result['errmsg'] = ''
        uplink_rate = float(re.split("[MK]+bps",result['uplink']['rate'])[0])
        uplink_packets_loss = result['uplink']['packets_loss'].split(":")[-1]
         
        downlink_rate = float(re.split("[MK]+bps",result['downlink']['rate'])[0])
        downlink_packets_loss = result['downlink']['packets_loss'].split(":")[-1]
        
        if "Kbps" in result['uplink']['rate']: 
            uplink_rate = uplink_rate / 1024
        if "Kbps" in result['downlink']['rate']: 
            downlink_rate = downlink_rate / 1024
        
        if uplink_rate <= self.conf['min_rate'] or uplink_rate > self.conf['max_rate']:
            result['errmsg'] = "Speedflex return incorrect speed uplink rate: %s" % result['uplink']['rate']
    
        if downlink_rate <= self.conf['min_rate'] or downlink_rate > self.conf['max_rate']:
            result['errmsg'] = "Speedflex return incorrect speed rate for downlink: %s" % result['downlink']['rate']
    
    
        if downlink_packets_loss != "0%" or uplink_packets_loss != "0%":
            result['errmsg'] = "Speedflex return high packets loss uplink packets loss[%s] - downlink packets loss[%s]" \
                                % (result['uplink']['packets_loss'], result['downlink']['packets_loss'])

        return result
 
