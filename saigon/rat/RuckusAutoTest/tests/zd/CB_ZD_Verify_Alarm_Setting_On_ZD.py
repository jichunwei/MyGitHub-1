"""
Description: This combo test is used to verify alarm settings on Zone Director by using Test button on configure page. 
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
Components required: 
    - Zone Director
Input: 
    - N/A
Output: 
    - PASS: If Zone Director return success after click on test button 
    - FAIL: If Zone Director return fail after click on test button 
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from copy import deepcopy
import logging


class CB_ZD_Verify_Alarm_Setting_On_ZD(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):        
        logging.info("Verify alarm setting by using test button")
        if not lib.zd.asz.test_alarm_settings(self.zd):
            self.errmsg = 'Zone Director can not send test email to mail server with current setting'
            return self.returnResult('PASS', self.errmsg)
        
        self.passmsg = 'Alarm Settings work properly on Zone Director with Test Button' 
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_status_timeout':120,}
        self.zd = self.testbed.components['ZoneDirector']
