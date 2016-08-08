"""
Description: This combo test is used to change traffic rate limit on all L3 switch port 
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - L3 Netgear Switch 
    
Input: 
    - N/A
Output: 
    - PASS: if rate limit can set successful 
    - FAIL: if any unexpect error return when set rate limit on switch  
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from pprint import pformat
import libZD_TestConfig as tconfig
import logging

class CB_ZD_Set_RateLimit_On_L3Switch(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        result = self._cfg_rate_limit()
        if self.errmsg: 
            return self.returnResult("FAIL", self.errmsg)
        return self.returnResult('PASS', result)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'timeout':5000,
                     'rate_limit': 100,
                     'port_range': '1/0/1-1/0/25'
                     }
        self.conf.update(conf)
        self.errmsg = ''
        self.l3_switch = self.testbed.components['L3Switch']
                
    def _cfg_rate_limit(self):
        try: 
            logging.info("Change rate limit on netgear switch to %s Mbps" % self.conf['rate_limit'])
            self.l3_switch.set_bandwidth(self.conf['port_range'], self.conf['rate_limit'])
        except Exception, e: 
            return "Fail to change rate limit on switch to %s - %s" % (self.conf['rate_limit'], e.message) 
        return "Set rate limit on switch to %s successful" % self.conf['rate_limit']
