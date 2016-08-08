"""
Description: check specified alarm in zd or not 
Author: west.li
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from copy import deepcopy
import logging, time, pdb


class CB_ZD_SR_Check_Alarm(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        # Get the Alarms list on the ZD
        alarms_list = []
        t1 = time.time() # Record the time before get date time information from the device
        t2 = time.time() - t1
        alarm_found=False
        
        logging.info('Getting Alarms information on the ZD')
        
        while not alarm_found and t2 < self.conf['timeout']:
            t2 = time.time() - t1
            zd1found=self._check_msg(self.zd1, self.zd1msg)
            zd2found=self._check_msg(self.zd2, self.zd2msg)
            if zd1found:
                self.carrierbag['activity_str']=self.zd1msg
                alarm_found=True
            if zd2found:
                self.carrierbag['activity_str']=self.zd2msg
                alarm_found=True
        if not alarm_found:
            return self.returnResult('FAIL', 'the expected alarm not found within %s seconds'\
                   % repr(self.conf['timeout']))
        
        return self.returnResult('PASS', 'the alarm (%s) found in %s seconds'%(self.carrierbag['activity_str'],t2))

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'timeout':7200,}
        self.conf.update(conf)
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        
        alarm_dict=self.zd1.messages
        alarm_msg =alarm_dict[self.conf['alarm']]
        
        if '{peer-ip}' in alarm_msg:
            self.zd1msg=self._get_msg(self.zd1, alarm_msg)
            self.zd2msg=self._get_msg(self.zd2, alarm_msg)
        
        
    def _get_msg(self,zd,msg):
        if zd.ip_addr=='192.168.0.2':
            peer_ip='[192.168.0.3]'
        else:
            peer_ip='[192.168.0.2]'
            # in SR related case,replace peer ip
        alarm_msg=msg.replace('{peer-ip}',peer_ip)
        return alarm_msg
    
    def _check_msg(self,zd,msg):
        logging.info('try to get alarm %s in zd %s'%(msg,zd.ip_addr))
        alarms_list = zd.get_alarms(msg)
        if len(alarms_list)>0:
            return True
        return False
        
                
        
        
        
        
        