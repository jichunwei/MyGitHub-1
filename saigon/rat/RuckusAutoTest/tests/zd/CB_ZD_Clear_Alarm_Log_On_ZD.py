"""
Description: This combo test is used to clear all current alarm logs on Zone Director 
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - Zone Director
Input: 
    - N/A
Output: 
    - PASS: If all log on Zone Director clear successful  
    - FAIL: If any log on Zone Director can not be clear 
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from copy import deepcopy
import logging, time

class CB_ZD_Clear_Alarm_Log_On_ZD(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        logging.info("Clear all alarm log on Zone Director")
        self.zd.clear_all_alarms()
        #@zj 20140717 fix zf-9200
        if self.ell == True:
            self.zd.clear_all_events()
        #@zj 20140717 fix zf-9200
        return self.returnResult('PASS', 'clear all alram successfully')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.ell = True
        self.conf = {'check_status_timeout':30,}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.has_key('zd'):
            self.zd=self.testbed.components[self.conf['zd']]
        #@zj 20140717 fix zf-9200
        #ell: Event Log Level
        #set default value
        if self.conf.has_key('ell'):
            self.ell = self.conf['ell']
