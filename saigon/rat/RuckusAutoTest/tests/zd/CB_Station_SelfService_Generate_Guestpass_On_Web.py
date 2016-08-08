'''
Description:
    Station generate guest pass  with self service on web
    put guest pass into carrierbag        
Create on 2015-4-15
@author: yanan.yu
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.components.lib.zd.release_compare import older_than_release


class CB_Station_SelfService_Generate_Guestpass_On_Web(Test):
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
        if self.conf['start_browser_before_auth']:
            self._start_browser_before_auth()
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
            
        self._generate_guestpass_with_selfservice_using_browser()
            
        if not self.conf.get("condition_allow"):
            if self.errmsg:
                self.passmsg = self.errmsg 
                self.errmsg = ""
            else:
                self.errmsg = self.passmsg
                
                
   
        if self.conf['close_browser_after_auth']:
            self._close_browser_after_auth()
        
        if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)


        return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        '''
        '''
        self._update_carrier_bag()
    

    def _init_test_params(self, conf):
        '''
        '''
        self.conf = {
            'sta_tag': "sta_1",
            'browser_tag': "browser",
            'browser_id':"",
            'start_browser_before_auth': True,
            'browser_name': "firefox",
            'close_browser_after_auth': True,
            'check_status_timeout': 100,
            'start_browser_tries': 3,
            'start_browser_timeout': 15,
            
            'use_tou': False,#Terms of Use
            'use_tac':False,#Terms and Conditions
            'tac_text':None,
            'redirect_url': "",
            'target_url': const.TARGET_IPV4_URL,
            'user_register_infor':{'username':'test.user','email':'test.user@163.com','countrycode':'','mobile':''},
            'clear_mobile':False, #clean up default value
            'guest_pass': "",
            'no_auth': False,
            'expected_data': "It works!",
            'condition_allow':True,
        }
        
        self.conf.update(conf)

        self.sta_tag = self.conf['sta_tag']
        self.browser_tag = self.conf['browser_tag']
  
        self.zd = self.testbed.components['ZoneDirector']
        
        #@author: yuyanan @since: 2015-7-28 @change:9.12.1 behavior change,remove mobile textbox when select screeen on zd
        zd_version = self.zd.get_version()
        self.mobile_exist_flag = older_than_release(zd_version,'9.12.1.0')
        self.conf.update({'mobile_exist_flag':self.mobile_exist_flag})
        
        
        self.selfservice_guestpass = ""
        self.errmsg = ""
        self.passmsg = ""

    def _retrive_carrier_bag(self):
        '''
        '''
        if self.sta_tag:
            sta_dict = self.carrierbag.get(self.sta_tag)
            self.sta = sta_dict.get('sta_ins')
            
        if not self.sta or not self.sta_tag:
                raise Exception("No station provided.")
        
        if not self.conf['start_browser_before_auth']:
            if self.browser_tag:
                browser_dict = self.carrierbag.get(self.browser_tag)
                self.browser_id = browser_dict.get('browser_id')
            if not self.browser_id or not self.browser_tag:
                    raise Exception("No Browser provided.")
            

    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag['mobile_exist_flag']= self.mobile_exist_flag
        if self.selfservice_guestpass:
            self.carrierbag['guest_pass'] = self.selfservice_guestpass
           

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
            

        
        
    def _generate_guestpass_with_selfservice_using_browser(self):
        try:  
            messages = self.sta.generate_guestpass_with_selfservice_using_browser(self.browser_id, self.conf)
            messages = eval(messages)
            
            for m in messages.iterkeys():
                if messages[m]['status'] == False: 
                    self.errmsg += messages[m]['message'] + " "
            
            if self.errmsg:
                return
            
            self.selfservice_guestpass = messages['generate']['guestpass']
            self.passmsg = "generate guestpass with selfservice successfully."
            
        except Exception, ex:
            logging.info(ex)
            self.errmsg += ex
            
            
            

