'''
Description:
    Station update contact with guest pass on web
    Check update contact
            
Create on 2015-4-15
@author: yanan.yu
'''
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as CONST


class CB_Station_SelfService_Update_Contact(Test):
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
        try:
            #@author: yuyanan @since: 2015-8-4 @change:9.12.1 behavior change. remove mobile textbox on station
            if not self.conf.get('condition_allow') and not self.mobile_exist_flag: #invalid mobile need not test
                passmsg = "invalid mobile need not test on this version" 
                return self.returnResult("PASS", passmsg)
            
            self._update_contact_detail_on_sta()    
            if not self.conf.get('condition_allow'):    
                if self.errmsg:
                    self.passmsg = self.errmsg
                    self.errmsg = ""
                    return
                else:
                    self.errmsg = self.passmsg
                    
                
            if self.errmsg:
                return
                
            
            self._check_update_contact_detail_on_sta()
            if self.errmsg:
                return
            
        finally:
            if self.conf['close_browser_after_auth']:
                self._close_browser_after_auth()
                
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
            'sta_ins':"",
            'sta_tag': "",
            'browser_tag': "browser",
            'browser_name': "firefox",
            'start_browser_before_auth': True,
            'close_browser_after_auth': True,
            'check_status_timeout': 100,
            'start_browser_tries': 3,
            'start_browser_timeout': 15,
            
            'target_url': CONST.TARGET_IPV4_URL,
            'user_register_infor':{'username':'test.user','email':'test.user@163.com','countrycode':'','mobile':''},
            'browser_id':"",
            'clear_mobile':False, #clean up default value
            'guest_pass': "",
            'use_tou': False,#Terms of Use
            'use_tac':False,#Terms and Conditions
            'redirect_url': "",
            'no_auth': False,
            'expected_data': "It works!",
            'condition_allow':True,
             }
        
        self.conf.update(conf)

        self.sta_tag = self.conf['sta_tag']
        self.email = self.conf['user_register_infor']['email']
        self.username = self.conf['user_register_infor']['username']
        self.countrycode = self.conf['user_register_infor']['countrycode']
        self.mobile = self.conf['user_register_infor']['mobile']
        self.phone = self.countrycode + self.mobile
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ""
        self.passmsg = ""

    def _retrive_carrier_bag(self):
        '''
        '''
        self.sta = self.conf.get('sta_ins')
        if not self.sta and self.sta_tag:
            sta_dict = self.carrierbag.get(self.sta_tag)
            self.sta = sta_dict.get('sta_ins')

        if not self.sta:
            raise Exception("No station provided.")


        self.guest_pass = self.carrierbag.get('guest_pass')
        #@author: yuyanan @since: 2015-7-28 @change:9.12.1 behavior change,remove mobile textbox when select screeen on zd
        self.mobile_exist_flag = self.carrierbag.get('mobile_exist_flag')
        
        self.conf.update({'guest_pass':self.guest_pass,
                          'mobile_exist_flag':self.mobile_exist_flag,})

        if not self.conf['start_browser_before_auth']:
            self.browser_id = self.conf.get('browser_id')
            if not self.browser_id:
                browser_dict = self.carrierbag.get(self.conf['browser_tag'])
                self.browser_id = browser_dict.get('browser_id')
    
            if not self.browser_id:
                raise Exception("No Browser provided.")
            


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
            
    def _update_contact_detail_on_sta(self):
        try:
            if self.guest_pass and self.email:
                messages = self.sta.update_selfservice_contact_using_browser(self.browser_id, self.conf)
                messages = eval(messages)
                for m in messages.iterkeys():
                    if messages[m]['status'] == False: 
                        self.errmsg += messages[m]['message'] + " "
            
                if self.errmsg:
                    return
            else:
                self.errmsg = "sorry,please provide your guestpass and email"
                
            self.passmsg += 'update client contact detail successfully.'   
            
        except Exception, ex:
            self.errmsg += ex.message 
        
            
            
    def _check_update_contact_detail_on_sta(self):
        
        expect = {'mobile':self.phone,'username':self.username,'email':self.email}
        if not self.mobile_exist_flag:
            expect.update({'mobile':''})
        try:
            messages = self.sta.get_selfservice_contact_using_browser(self.browser_id, self.conf)
            messages = eval(messages)
            logging.info("get contact messages :%s" % messages)
            for m in messages.iterkeys():
                if messages[m]['status'] == False: 
                        self.errmsg += messages[m]['message'] + " "

            if self.errmsg:
                    return
                
            actual_dict = messages.get('get_contact').get('contact_detail_dict')
            for key in expect:
                if expect[key] == actual_dict[key]:
                    continue 
                else:
                    self.errmsg += "expect value is [%s],but actual value is [%s]"%(expect[key],actual_dict[key])
             
            if self.errmsg:
                    return
            
            self.passmsg += 'check update client contact detail successfully.' 
                    
        except Exception, ex:
            self.errmsg += ex.message  
            

        
        
        
        
        
