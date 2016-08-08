# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to generate roaming
Author: Jason Lin
Email: jlin@ruckuswireless.com
Test Parameters: {'repeat': generate roaming times,
                  'shieldbox1:{'ap': mac addr of AP in shieldbox1,
                               'db': attenuation value setting for client roaming to ap of shieldbox2,
                               'ruca_id': id of super ruca in shieldbox1},
                  'shieldbox2:{'ap': mac addr of AP in shieldbox2
                               'db': attenuation value setting for client roaming to ap of shieldbox1
                               'ruca_id': id of super ruca in shieldbox2}
                  }
example:{'repeat': 10, 
         'shieldbox1': {'ap': u'00:1f:41:2a:b8:b0', 
                        'db': '34', 
                        'ruca_id': ['0']}, 
         'shieldbox2': {'ap': u'00:22:7f:02:49:40', 
                        'db': '34', 
                        'ruca_id': ['1']}}
Result type:PASS/FAIL
Results:PASS:generated client roaming between APs
        FAIL:
                  
Test Procedure:
1. config:
   - 
2. test:
   - press dail key on phone
   - adjust ruca attunation to force phone roaming between APs in shieldbox1 and shieldbox2 
3. cleanup:
   - 
"""
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.scripts.zd import spectralink_phone_config as ph_cfg
class CB_ZD_Generate_Roaming(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):      
        self._generateRoaming()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        #self._turn_off_phone()
        msg = 'Generate Roaming [%d] times completed' % self.conf['repeat']
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
    #{'shieldbox1':{'ruca_id':['0'], 'ap':'xx:xx:xx:xx:xx:xx', 'db':'34'},
    # 'shieldbox2':{'ruca_id':['1'], 'ap':'yy:yy:yy:yy:yy:yy', 'db':'34'}, 'repeat':10}
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        self.conf = conf.copy()
        self.active_phone_cfg = ph_cfg.get_ph_cfg(self.conf['phone'])
        self.phone = self.active_phone_cfg['ssid']
        self.pwr_key = self.end_key = self.active_phone_cfg['pwr_key']
        self.send_key = self.active_phone_cfg['send_key']
        self.push_dev = self.testbed.components['PushKeypadDevice']
        
    def _setAttenuator(self, id, db):
        for idx in id:
            #cmdline = 'rac -i%s -v%s' % (idx, db)
            #logging.debug("set Attenuator cmd %s" % cmdline)
            #output = subprocess.Popen(cmdline,  stdout=subprocess.PIPE).communicate()[0]
            utils.set_super_ruca_attenuation(idx, db)
        
    def _get_active_ap_mac(self):
        client_info = tmethod.get_active_client_by_mac_addr(self.active_phone_cfg['mac_addr'], self.zd)
        if client_info:
            return client_info['apmac']
        else:
            logging.info('phone[%s] is not shown on ZD' % self.active_phone_cfg['mac_addr'])
            self.errmsg = 'phone[%s] is not shown on ZD' % self.active_phone_cfg['mac_addr']
         
    
    def _generateRoaming(self):
        print('\a\a\a')
        #raw_input("Press SEND Key on Speckralink Phone [%s]" % self.conf['phone'])
        self.push_dev.push_send_key(self.send_key)
        for p in range(0, self.conf['repeat'], 
                       2):
            #active_ap = self._get_active_ap_mac()
            logging.debug("[roaming %s] making phone[%s] roaming from box1 to box2" % (str(p+1), self.conf['phone']))
            #if active_ap == self.conf['box1']['ap']:
            for i in range(1, int(self.conf['box1']['db'])+1):
                self._setAttenuator(id=self.conf['box2']['ruca_id'], db=int(self.conf['box1']['db'])-i)
                self._setAttenuator(id=self.conf['box1']['ruca_id'], db=i)
                time.sleep(0.5)
            logging.debug("[roaming %s] making phone[%s] roaming from box2 to box1" % (str(p+2), self.conf['phone']))            
            for i in range(1, int(self.conf['box2']['db'])+1):
                self._setAttenuator(id=self.conf['box1']['ruca_id'], db=int(self.conf['box2']['db'])-i)
                self._setAttenuator(id=self.conf['box2']['ruca_id'], db=i)
                time.sleep(0.5)
            
            tmethod8.pause_test_for(1, 'Wait for Spectralink Phone[%s] roam to another AP' % self.conf['phone'])
            
    def _turn_off_phone(self):
        logging.info('push end key of phone [%s] to stop traffic' % self.phone )
        self.push_dev.push_end_key(self.end_key)
        logging.info('turn off phone [%s]' % self.phone)
        self.push_dev.turn_off_phone(self.pwr_key)

