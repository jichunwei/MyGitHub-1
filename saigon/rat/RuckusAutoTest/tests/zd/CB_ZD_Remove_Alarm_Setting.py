"""
Description: This combo test is used to clear current alarm setting on Zone Director 
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - Zone Director
Input: 
    - N/A
Output: 
    - PASS: If within timeout, there is an alarm log was triggered  
    - FAIL: If within timeout, there is no alarm log was triggered 
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from copy import deepcopy
import logging


class CB_ZD_Remove_Alarm_Setting(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        try:
            logging.info("Clear all alarm on Zone Director")
            lib.zd.asz.clear_alarm_settings(self.zd)
        except Exception, e: 
            logging.debug(e.message)
            return self.returnResult('FAIL', e.message)
        return self.returnResult('PASS', '')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'timeout':300,}
        self.zd = self.testbed.components['ZoneDirector']
        
 
