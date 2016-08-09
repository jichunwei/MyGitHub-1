'''
Description:
    Verify the station can not authenticate with expired guest passes.

Warning:
    This script uses the old RatToolAgent.
       
Create on 2011-8-26
@author: serena.tan@ruckuswireless.com
'''


import time
import logging

from RuckusAutoTest.models import Test
import libZD_TestConfig as tconfig


class CB_Station_Verify_Invalid_GuestPass(Test):
    required_components = ['ZoneDirector', 'Station']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        time.sleep(5)
        logging.info("Perform Guest Auth on the station %s" % self.conf['sta_tag'])

        try:
            arg = tconfig.get_guest_auth_params(self.zd, 
                                                self.guest_pass, 
                                                self.conf['use_tou'], 
                                                self.conf['redirect_url'])
            
            if self.conf['target_url']:
                arg['target_url'] = self.conf['target_url']

            if self.conf['expected_data']:
                arg['expected_data'] = self.conf['expected_data']

            arg['no_auth'] = bool(self.conf['no_auth'])

            messages = self.sta.perform_guest_auth_using_browser(self.browser_id, arg)
            messages = eval(messages)

            for m in messages.iterkeys():
                if messages[m]['status'] == False:
                    self.passmsg = "Guest authentication can not be done while the Guest Pass had expired"

                else:
                    self.errmsg = "Guest authentication can be done while the Guest Pass had expired."

        except Exception, e:
            self.errmsg = "Fail to verify guest authentication with invalid guest pass: %s" % e.message

        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'sta_tag': '',
                     'browser_tag': 'browser',
                     'browser_id': '',
                     'use_tou': False,
                     'no_auth': False,
                     'guest_pass': '',
                     'target_url': 'http://172.16.10.252/',
                     'redirect_url': '',
                     'expected_data': 'It works!'
                     }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        self.sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        if not self.conf['guest_pass']:
            self.guest_pass = self.carrierbag['guest_pass']
        
        if not self.conf['browser_id']:
            browser_dict = self.carrierbag.get(self.conf['browser_tag'])
            self.browser_id = browser_dict.get('browser_id')
  
    def _update_carribag(self):
        pass
