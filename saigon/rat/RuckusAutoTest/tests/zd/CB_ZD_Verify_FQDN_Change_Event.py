# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: ccheng@ruckuswireless.com
   @since: May-24, 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       -'zd_tag': "zd tag. Will get zd components via zd tag in self.testbed.components",
       -'enabled': 'Enable or disable limited zd discoverty',
       -'access_ip': 'IP of machine access to zd',
       -'pri_zd_addr': 'Primary ZD ip or domain name',
       -'sec_zd_addr': 'Secondary ZD ip or domain name',
       -'timeout': 'timeout to verify event',
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Verify setting change event is correct
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Change event is correct.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import time
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Verify_FQDN_Change_Event(Test):
    required_components = ['ZoneDirector']
    parameters_description = {'zd_tag': "zd tag. Will get zd components via zd tag in self.testbed.components",
                              'enabled': 'Enable or disable limited zd discoverty',
                              'access_ip': 'IP of machine access to zd',
                              'pri_zd_addr': 'Primary ZD ip or domain name',
                              'sec_zd_addr': 'Secondary ZD ip or domain name',
                              'timeout': 'timeout to verify event',
                              }
    
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self._verify_event_fqdn_change()
            
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Verify FQDN change event successfully"
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(zd_tag = '',
                         enabled = True,  
                         access_ip = '',
                         pri_zd_addr = '',
                         sec_zd_addr = '',
                         timeout = 60,
                         )
        self.conf.update(conf)
        
        zd_tag = self.conf.pop('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']
            
        self.errmsg = ''
        self.passmsg = ''
        
    def _verify_event_fqdn_change(self):
        '''
        Verify fqdn change event in zd.
        '''
        try:
            errmsg = ''
            en_msg_ptn, dis_msg_ptn = self._get_event_temp()
            
            if self.conf['enabled']:
                msg_ptn = en_msg_ptn
                
                msg_ptn = msg_ptn.replace('{pri_zd_addr}', self.conf['pri_zd_addr'].lower())
                if self.conf['sec_zd_addr']:
                    msg_ptn = msg_ptn.replace('{sec_zd_addr}', self.conf['sec_zd_addr'].lower())
                else:
                    msg_ptn = msg_ptn.replace(' and secondary ZoneDirector [{sec_zd_addr}]', '')
            else:
                msg_ptn = dis_msg_ptn
                
            msg_ptn = msg_ptn.replace('{access_ip}', self.conf['access_ip'])
            
            logging.info("Expect event %s" % msg_ptn)
                
            cur_time = time.time()
            timeout = self.conf['timeout']
            while time.time() - cur_time < timeout:
                logging.info("Get all events from ZD")
                events_log = self.zd.get_events()
                
                logging.debug("All events in ZD:%s" % events_log)
                
                logging.info("Verify expect event in event logs")
                fnd = False
                for event in events_log:
                    if msg_ptn in event:
                        fnd = True
                        break
                    
                if not fnd:
                    time.sleep(5)
                    errmsg = "Didn't found any event log [%s]" % msg_ptn
                else:
                    break
                
            if errmsg:
                self.errmsg = errmsg
            
        except Exception, e:
            self.errmsg = "Fail to verify event: %s" % e.message
        
    def _get_event_temp(self):
        '''
        Get event template from messages of zd via type.
        '''
        en_message_type = 'fqdn' #Will be updated after the developer add message to bin/messages.
        dis_message_type = 'fqdn' #Will be updated after the developer add message to bin/messages.
        zd_all_messages = self.zd.messages
        
        if zd_all_messages.has_key(en_message_type):
            enable_ptn = zd_all_messages[en_message_type]
        else:
            enable_ptn = "Admin from [{access_ip}] change to provision all AP's with primary ZoneDirector [{pri_zd_addr}] and secondary ZoneDirector [{sec_zd_addr}]"
            
        if zd_all_messages.has_key(dis_message_type):
            disable_ptn = zd_all_messages[dis_message_type]
        else:
            disable_ptn = "Admin from [{access_ip}] remove AP's primary and secondary ZoneDirector settings"
                
        return enable_ptn, disable_ptn