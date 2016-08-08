"""
Description: This combo test is used to wait for Alarm was trigger on Zone Director  
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
import logging, time, pdb


class CB_ZD_Waiting_Alarm_Trigger(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        # Get the Alarms list on the ZD
        alarms_list = []
        t1 = time.time() # Record the time before get date time information from the device
        t2 = time.time() - t1
        
        logging.info('Getting Alarms information on the ZD')
        while len(alarms_list) < 1 and t2 < self.conf['timeout']:
            alarms_list = self.zd.get_alarms()
            time.sleep(10)
            t2 = time.time() - t1
    
        if len(alarms_list) < 1:
            return self.returnResult('FAIL', 'Test case has not completed. There is no Alarm generated within %s s'\
                   % repr(self.conf['timeout']))
        
        return self.returnResult('PASS', '')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'timeout':5000,}
        self.zd = self.testbed.components['ZoneDirector']
        
 
