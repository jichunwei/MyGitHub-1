'''
Created on Jan 24, 2014

@author: jacky luh
'''
'''
'''
import logging
import time

from RuckusAutoTest.models import Test
import libZD_TestConfig as tconfig


class CB_ZD_Perform_Guest_Auth(Test):
    '''
    classdocs
    '''


    def config(self, conf):
        '''
        '''
        self._init_test_params(conf)
        self._retrive_carrier_bag()


    def test(self):
        '''
        '''
        self._start_browser_before_auth()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
            
        self._perform_guest_auth()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)

        time.sleep(5)
        self._close_browser_after_auth()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
            
        self._update_carrier_bag()

        return self.returnResult("PASS", self.passmsg)


    def cleanup(self):
        '''
        '''
        pass
    

    def _init_test_params(self, conf):
        '''
        '''
        self.carrierbag_keys = {
            'sta_ins_attr': "station",
            'guest_pass_attr': "guest_pass",
            'use_tou_attr': "use_tou",
            'redirect_url_attr': "redirect_url",
        }
        if conf.has_key('carrierbag_keys'):
            self.carrierbag_keys.update(conf['carrierbag_keys'])
            conf.pop('carrierbag_keys')

        self.sta_ins_attr = self.carrierbag_keys['sta_ins_attr']
        self.guest_pass_attr = self.carrierbag_keys['guest_pass_attr']
        self.use_tou_attr = self.carrierbag_keys['use_tou_attr']
        self.redirect_url_attr = self.carrierbag_keys['redirect_url_attr']

        self.conf = {
            self.guest_pass_attr: "",
            self.use_tou_attr: False,
            self.redirect_url_attr: "",
            'check_status_timeout': 100,
            'target_url': "http://172.16.10.252/",
            'no_auth': False,
            'expected_data': "It works!",
            'browser_name': "firefox",
            'start_browser_tries': 3,
            'start_browser_timeout': 15,
        }
        self.conf.update(conf)

        self.redirect_url = self.conf[self.redirect_url_attr]

        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ""
        self.passmsg = ""


    def _retrive_carrier_bag(self):
        '''
        '''
        self.sta = self.carrierbag.get(self.sta_ins_attr)

        if not self.sta:
            raise Exception("No station provided.")


        self.guest_pass = self.conf.get(self.guest_pass_attr)
        if not self.guest_pass:
            self.guest_pass = self.carrierbag.get(self.guest_pass_attr)

        if not self.guest_pass:
            raise Exception("No Guest Pass provided.")
            

    def _update_carrier_bag(self):
        '''
        '''
        pass


    def _perform_guest_auth(self):
        '''
        '''
        logging.info("Perform Guest Auth on the station")

        try:
            arg = tconfig.get_guest_auth_params(
                self.zd, self.guest_pass, self.conf[self.use_tou_attr], self.redirect_url
            )
            if self.conf.get('target_url'):
                arg['target_url'] = self.conf['target_url']

            if self.conf.get('expected_data'):
                arg['expected_data'] = self.conf['expected_data']

            arg['no_auth'] = bool(self.conf.get('no_auth'))

            messages = self.sta.perform_guest_auth_using_browser(self.browser_id, arg)
            messages = eval(messages)

            for m in messages.iterkeys():
                if messages[m]['status'] == False:
                    self.errmsg += messages[m]['message'] + " "

                else:
                    self.passmsg += messages[m]['message'] + " "

            if self.errmsg:
                return

            self.passmsg += \
                "Perform Guest Auth successfully on station."
            logging.info(self.passmsg)

        except Exception, e:
            self.errmsg += e.message
            logging.info(self.errmsg)


    def _start_browser_before_auth(self):
        '''
        Start browser in station.
        '''
        try:
            logging.info("Try to start a browser on station")
            self.browser_id = self.sta.init_and_start_browser(self.conf['browser_name'],
                                                              self.conf['start_browser_tries'], 
                                                              self.conf['start_browser_timeout'])
            self.browser_id = int(self.browser_id)
            self.passmsg += "The browser on station was started successfully with ID"        

        except Exception, ex:
            self.errmsg += ex.message
    
    
    def _close_browser_after_auth(self):
        try:
            logging.info("Try to close the browser on station")
            self.sta.close_browser(self.browser_id)
            self.passmsg += 'Close browser on station successfully.'
        except Exception, ex:
            self.errmsg += ex.message
            
