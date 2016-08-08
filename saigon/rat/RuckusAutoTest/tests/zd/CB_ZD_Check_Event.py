"""
Description: check specified event in zd or not 
Author: west.li
"""

import logging
from RuckusAutoTest.models import Test


class CB_ZD_Check_Event(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        event_list=self.zd.get_events()
        event_fonud=False
        for event in event_list:
            if self.event_msg == str(event[3]):
                event_fonud=True
                break
        #@author: Jane.Guo @since: 2013-11 add a parameter "negative" to check event doesn't exist
        if not event_fonud:
            if not self.negative:
                return self.returnResult("FAIL", 'event not found, correct behavior')
            else:
                return self.returnResult('PASS', 'the event (%s) not found, correct behavior'%self.event_msg)
        else:
            if not self.negative:
                return self.returnResult('PASS', 'the event (%s) found successfully'%self.event_msg)
            else:
                return self.returnResult("FAIL", 'event found, wrong behavior')

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {
                     'te_addr':'192.168.0.10',
                     'negative': False,
                     }
        self.conf.update(conf)
        self.negative = self.conf.get('negative')
        
        self.te_addr=self.conf['te_addr']
        if self.conf.has_key('user'):
            self.user=self.conf['user']
        if self.conf.has_key('server_name'):
            self.server_name=self.conf['server_name']
            
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.has_key('zd'):
            self.zd=self.carrierbag[self.conf['zd']]
        
        logging.info("check alarm in zd %s"%self.zd.ip_addr)
        message=self.zd.messages
        #@author: Jane.Guo @since: 2013-11 add a scenario if event is just a sentence
        if self.conf['event'] in ['MSG_admin_login_failed','MSG_admin_login','MSG_admin_logout']:
            event_msg =message[self.conf['event']]
            event_msg=event_msg.replace('{admin}','Admin[%s]'%self.user)
            event_msg=event_msg.replace('{ip}','[%s]'%self.te_addr)
        elif self.conf['event'] in ['MSG_AUTHSVR_created','MSG_AUTHSVR_modified','MSG_AUTHSVR_deleted']:
            event_msg =message[self.conf['event']]
            event_msg=event_msg.replace('{authsvr}','Authentication/Accounting Server[%s]'%self.server_name)
            event_msg=event_msg.replace('{ip}','[%s]'%self.te_addr)
        else:
            event_msg=self.conf['event']
        
        self.event_msg=event_msg
        logging.info("expected msg is '%s'"%self.event_msg)
        
