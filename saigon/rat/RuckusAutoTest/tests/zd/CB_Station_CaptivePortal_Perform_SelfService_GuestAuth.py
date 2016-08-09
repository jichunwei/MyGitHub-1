'''
Description:
    Stationb perform  guest access with self service  wlan authorize on Web.
       
Create on 2015-4-15
@author: yanan.yu
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as CONST

class CB_Station_CaptivePortal_Perform_SelfService_GuestAuth(Test):
    
    def config(self, conf):
        '''
        '''
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)


    def test(self):
        '''
        '''
        if self.conf['start_browser_before_auth']:
            self._start_browser_before_auth()
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
        
        
        self._perform_guest_auth()
        if self.errmsg:
            if not self.conf.get('condition_allow'):
                self.errmsg = ""
                self.passmsg = "this is a invalid guestpass."
                

        if self.conf['close_browser_after_auth']:
            time.sleep(5)
            self._close_browser_after_auth()
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
            
        self._update_carrier_bag()
        
        if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)

        return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        '''
        '''
        pass
    

    def _init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_tag': "",
            'browser_id':"",
            'browser_tag': "browser",
            'start_browser_before_auth': True,
            'browser_name': "firefox",
            'close_browser_after_auth': True,
            'check_status_timeout': 100,
            'start_browser_tries': 3,
            'start_browser_timeout': 15,
            
            'redirect_url': "",
            'target_url': CONST.TARGET_IPV4_URL,
            'guest_pass': "",
            'use_tou': False,#Terms of Use
            'use_tac':False,#Terms and Conditions
            'no_auth': False,
            'expected_data': "It works!",
            'user_register_infor':{'username':'test.user','email':'test.user@163.com','countrycode':'','mobile':''},
           
            'clear_mobile':False, #clean up default value
            'condition_allow':True,
            'duration': 1,
            'duration_unit': 'Days',
            'check_access_duration':False,
            'guest_auth_cfg': {'use_tou': False}, 
            'sta_mac':None,
        }
        
        self.conf.update(conf)#no sure this is ok!

        self.sta_tag = self.conf['sta_tag']
        self.email = self.conf['user_register_infor']['email']
        self.username = self.conf['user_register_infor']['username']
        self.countrycode = self.conf['user_register_infor']['countrycode']
        self.mobile = self.conf['user_register_infor']['mobile']
        self.phone = self.countrycode + self.mobile
        
        self.sta_tag = self.conf['sta_tag']
        self.browser_tag = self.conf['browser_tag']
        
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ""
        self.passmsg = "sta perform authorize successfully"

    def _retrive_carrier_bag(self):
        '''
        '''
        if self.sta_tag:
            sta_dict = self.carrierbag.get(self.sta_tag)
            self.sta = sta_dict.get('sta_ins')
            sta_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
            self.conf.update({'sta_mac':sta_mac})
            
        if not self.sta or not self.sta_tag:
                raise Exception("No station provided.")
        
 
        
        self.guest_pass = self.conf.get('guest_pass')
        if not self.guest_pass:
            self.guest_pass = self.carrierbag.get('guest_pass') 
            if not self.guest_pass:
                self.errmsg = "sorry,your guest pass is null,please provide guest pass"
            
        self.conf.update({'guest_pass':self.guest_pass})
                
        if not self.conf['start_browser_before_auth']:
            if self.browser_tag:
                browser_dict = self.carrierbag.get(self.browser_tag)
                self.browser_id = browser_dict.get('browser_id')
            if not self.browser_id or not self.browser_tag:
                raise Exception("No Browser provided.")
        
   

    def _update_carrier_bag(self):
        '''
        '''
        pass
        
 
    def _perform_guest_auth(self):
        '''
        '''
        logging.info("Perform Guest Auth on the station %s" % self.sta_tag)

        try:
            messages = self.sta.perform_self_service_guest_auth_using_browser(self.browser_id, self.conf)
            messages = eval(messages)
            
            for m in messages.iterkeys():
                if messages[m]['status'] == False:   
                    self.errmsg += messages[m]['message'] + " "
                else:
                    self.passmsg += messages[m]['message'] + " "
                    
            if self.errmsg:
                return
       
            self.passmsg = "Perform Guest Auth successfully on station [%s]." % self.sta_tag
                
            logging.info(self.passmsg)

        except Exception, e:
            self.errmsg += e.message
            logging.info(self.errmsg)


    def _start_browser_before_auth(self):
        '''
        Start browser in station.
        '''
        try:
            logging.info("Try to start a %s browser on station[%s]" \
                        % (self.conf['browser_name'], self.sta_tag))
            self.browser_id = self.sta.init_and_start_browser(self.conf['browser_name'],
                                                              self.conf['start_browser_tries'], 
                                                              self.conf['start_browser_timeout'])
            self.browser_id = int(self.browser_id)
            self.passmsg += "The %s browser on station '%s' was started successfully with ID[%s]" \
                              % (self.conf['browser_name'], self.sta_tag, self.browser_id)            

        except Exception, ex:
            self.errmsg += ex.message
    
    
    def _close_browser_after_auth(self):
        try:
            logging.info("Try to close the browser with ID[%s] on station[%s]" \
                         % (self.browser_id, self.sta_tag))
            self.sta.close_browser(self.browser_id)
            self.passmsg += 'Close browser with ID[%s] on station[%s] successfully.' \
                            % (self.browser_id, self.sta_tag)
        
        except Exception, ex:
            self.errmsg += ex.message
            

        
        
        
        
        
