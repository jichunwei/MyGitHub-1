'''
Description:
    Self service Guest pass related method.
       
Create on 2015-4-15
@author: yanan.yu
'''
import types
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException 
from client_auth.CaptivePortal import CaptivePortal
import re
from urllib import *

TIMEOUT = 3600*5

class SelfServiceGuestAuth(CaptivePortal):
    '''
    classdocs
    '''

    locators = {
                'guestpass_textbox': r"//input[@name='key']",
                'login_button': r"//input[@name='ok']",
                'login_failed': r"//div[@id='loginfailed']",
                'redirect_url': r"//a[@id='redirecturl']",
                'tou_button': r"//input[@id='acceptBtn']",
                'guestpass_button':r"//input[@id='guest']",
                }
    
    locators_self_service = {
                             'guestpass_textbox':r"//input[@id='key']",
                             'username_textbox':r"//input[@id='name']",
                             'email_textbox':r"//input[@id='email']",
                             'countrycode_textbox':r"//input[@id='countrycode']",
                             'mobile_textbox':r"//input[@id='mobile']",
                             'submit_button': r"//input[@id='t1']",
                             'login_button': r"//input[@type='submit']",
                             'goto_portal_button_with_guestpass':r"//a[@id='togoA']",
                             'guestpass':r"//p[@id='guest_pass_con']",
                             'regist_new_guestpass_url':u'/selfguestpass/guestRegistration.jsp?cookie=&redirecturl=%s',
                             'update_contact_detail':u'/selfguestpass/updateLogin.jsp?cookie=&redirecturl=%s',
                             'login_failed':r"//div[h1='Invalid Guest Pass']",
                             'terms_and_condition_textbox':r'//pre[@id="terms"]',
                             'max_device_text':r"//div[h1='Maximum Device Reached']",
                             'access_button':r"//input[@id='access']",
                             'select_onePC_checkbox':r'//tr[td="%s"]//input',
                             'portal_page_title':r"//div[h1='Welcome to the Guest Access login page.']",
                             'new_guest_regist_title':r"//div[h1='New Guest Registration']",
                             }
    
    locators_update_contact = {
                               'guestpass_textbox':r"//input[@id='guestPassword']",
                               'email_textbox':r"//input[@id='emailLogin']",
                               'update_detail_button':r"//input[@id='updateDetail']",
                               'new_name_textbox':r"//input[@id='newName']",
                               'countrycode_textbox':r"//input[@id='countrycode']",
                               'new_mobile_textbox':r"//input[@id='newMobile']",
                               'update_button':r"//input[@id='btUpdate']",
                               'old_username_label':r"//p[@id='name']",
                               'old_mobile_label':r"//p[@id='mobile']",
                               }


    def __init__(self):
        '''
        Constructor
        '''
        super(SelfServiceGuestAuth, self).__init__()
        
        
    def _get_expect_url(self,xpath,params):
        messages = {}
     
        print "wait open url :%s"%self.params['dest_url']
        
        if not self.wait_url_appear(self.locators_self_service['portal_page_title'],self.params['dest_url'],):
            messages.update({
                            'get_url': {
                                        'status': False,
                                        'message':'can not open url:%s'%self.params['dest_url'],
                                        }
                            })
            return messages
   
        current_url = self.browser.current_url
        index = current_url.find("selfguestpass")  
        sub_url_zd = current_url[0:index - 1]  #get https://192.168.128.2/        
        sub_url = xpath % params
        expect_url = sub_url_zd + sub_url
        print "expect_url-->%s" % expect_url
                
        self.browser.get(expect_url) 
            
        messages.update({'get_url': { 'status': True,}})
             
        return messages
    
    def get_contact_detail(self):
        messages = {}
        try:
            
            messages = self._get_expect_url(self.locators_self_service[ 'update_contact_detail'], self.params['redirect_url'])
            if not messages.get('get_url').get('status'):
                return messages
        
            textbox = self.browser.find_element_by_xpath(self.locators_update_contact['email_textbox'])
            textbox.send_keys(self.params['email'])
            
            textbox = self.browser.find_element_by_xpath(self.locators_update_contact['guestpass_textbox'])
            textbox.send_keys(self.params['guestpass'])
            
            button = self.browser.find_element_by_xpath(self.locators_update_contact['update_detail_button'])
            button.click()
            
            
            if self.wait_element_appear(self.locators_update_contact['old_username_label']):
                username = self.browser.find_element_by_xpath(self.locators_update_contact['old_username_label']).text
            else:
                messages.update({
                                  'get_contact': {
                                                  'status': False,
                                                  'message':'Have not return web after click update button.',
                                                  }
                                  })
                
            
            if self.params['mobile_exist_flag']: 
                mobile = self.browser.find_element_by_xpath(self.locators_update_contact['old_mobile_label']).text
            else:
                mobile = ''
                
            contact_detail_dict = {'username':username,'mobile':mobile,'email':self.params['email'],'guestpass':self.params['guestpass']}
            
            messages.update({
            'get_contact': {
                'status': True,
                'contact_detail_dict':contact_detail_dict,
                        }
           })
        except NoSuchElementException, ex:
            messages.update({
            'get_contact': {
                'status': False,
                'message':ex.message,
                        }
           })
        
        return messages
         
         
    def update_contact_detail(self):
        messages = {}
        try:
          
            messages = self._get_expect_url(self.locators_self_service[ 'update_contact_detail'], self.params['redirect_url'])
            if not messages.get('get_url').get('status'):
                return messages
            
            textbox = self.browser.find_element_by_xpath(self.locators_update_contact['email_textbox'])
            textbox.send_keys(self.params['email'])
            
            textbox = self.browser.find_element_by_xpath(self.locators_update_contact['guestpass_textbox'])
            textbox.send_keys(self.params['guestpass'])
            
            button = self.browser.find_element_by_xpath(self.locators_update_contact['update_detail_button'])
            button.click()
            
            if self.wait_element_appear(self.locators_update_contact['new_name_textbox']):
                textbox = self.browser.find_element_by_xpath(self.locators_update_contact['new_name_textbox'])
                textbox.send_keys(self.params['username'])
            else:
                messages.update({
                                'update_contact': {
                                                    'status': False,
                                                    'message':"Have not return, after click update button first.",
                                                  }
                                })
                
                return messages
                
            
            #@author: yuyanan @since:2015-7-28 @change:9.12.1 behavior change, remove mobile textbox, when select screen on zd
            if self.params['mobile_exist_flag']:
                textbox = self.browser.find_element_by_xpath(self.locators_update_contact['countrycode_textbox'])
                textbox.clear()
                textbox.send_keys(self.params['countrycode'])
            
                textbox = self.browser.find_element_by_xpath(self.locators_update_contact['new_mobile_textbox'])
                textbox.clear()
                textbox.send_keys(self.params['mobile'])
            
            button = self.browser.find_element_by_xpath(self.locators_update_contact['update_button'])
            button.click()
            
        
            if self.wait_element_appear(self.locators_self_service['portal_page_title']):
                messages.update({'update_contact': {'status': True,} })
            else:
                messages.update({
                                'update_contact': {
                                                    'status': False,
                                                    'message':"Have not return, after click update button second.",
                                                  }
                                })
                
                return messages
                
 
        except NoSuchElementException, ex:
            try:
                errmsg = self.browser.find_element_by_id('tip').text
                messages.update({
                                 'update_contact': {
                                                    'status': False,
                                                    'message':errmsg+","+ex.message
                                                    }
                                 })
            except NoSuchElementException, ex:   
                messages.update({
                                 'update_contact': {
                                                    'status': False,
                                                    'message':ex.message+","+"tip can not find",
                                                    }
                                 })
    
        return messages
    
    def get_terms_and_condition(self):
        messages = {}
        try:    
            tac = self.browser.find_element_by_xpath(self.locators_self_service['terms_and_condition_textbox']).text
            messages.update({
            'tac': {
                'status': True,
                'value':tac,
                        }
           })
        except NoSuchElementException, ex:
            messages.update({
            'tac': {
                'status': False,
                'message':ex.message,
                        }
           })
            
        return messages
        
    def check_terms_and_condition(self):
       
        errmsg = ""
        messages = self.get_terms_and_condition()
        if messages['tac']['status'] == False: 
            return messages
        else:
            if messages['tac']['value'] == self.params.get("tac_text"):
                return messages                                                               
            else:
                errmsg = 'expect tac is [%s],but actual is [%s]'%(self.params.get("terms_and_condition"),messages['tac']['value'])
                messages.update({
                'tac': {
                    'status': False,
                    'message':errmsg,
                        }
                   })          
        return messages  
          
   
    def generate_guestpass_on_web(self,tries=3):
    
        count = 0
        guestpass = ""
        errmsg = "failed"

        while count < tries:
            print "try %s times generate guest pass......."%count
            count += 1
            messages = {}
            try:
                
                messages = self._get_expect_url(self.locators_self_service[ 'regist_new_guestpass_url'],self.params['redirect_url'])
                if not messages.get('get_url').get('status'):
                    return messages
            
                if self.params.get("use_tac"):
                    messages = self.check_terms_and_condition()
                    if messages['tac']['status'] == False:
                        print "fail,check use terms and condition"
                        return messages
                    print "check use terms and condition successfully"
                 
                # input register information
                textbox = self.browser.find_element_by_xpath(self.locators_self_service['username_textbox'])
                textbox.send_keys(self.params['username'])
            
                textbox = self.browser.find_element_by_xpath(self.locators_self_service['email_textbox'])
                textbox.send_keys(self.params['email'])
            
                #@author: yuyanan @since:2015-7-28 @change:9.12.1 behavior change, remove mobile textbox, when select screen on zd
                if self.params['mobile_exist_flag']:
                    textbox = self.browser.find_element_by_xpath(self.locators_self_service['countrycode_textbox'])
                    if self.params['clear_mobile']:
                        textbox.clear()
                    textbox.send_keys(self.params['countrycode'])
            
                    textbox = self.browser.find_element_by_xpath(self.locators_self_service['mobile_textbox'])
                    if self.params['clear_mobile']:
                            textbox.clear()
                    textbox.send_keys(self.params['mobile'])
              
            
                button = self.browser.find_element_by_xpath(self.locators_self_service['submit_button'])
                button.click()

                #check guestpass web is open
                if self.wait_element_appear('logo_title','id'):
                    if self.browser.find_element_by_id('logo_title').text in  ['Welcome to Guest Access']:
                        guestpass = self.browser.find_element_by_xpath(self.locators_self_service['guestpass']).text
                    else:
                        errmsg = self.browser.find_element_by_id('logo_title').text
                        messages.update({
                                     'generate': {
                                                  'status': False,
                                                  'message': errmsg,
                                                  }
                                     })
                        return messages
                else:
                    errmsg = "Can not generate guest pass. click submit button have not return"
                    messages.update({
                                     'generate': {
                                                  'status': False,
                                                  'message': errmsg,
                                                  }
                                     })
                    return messages
                    
                # check term and condition
                if self.params.get("use_tac"):
                    messages = self.check_terms_and_condition()
                    if messages['tac']['status'] == False:
                        print "fail, check use terms and condition"
                        return messages
                    print "check use terms and condition successfully"
                
                messages.update({
                                 'generate': {
                                              'status': True,
                                              'guestpass': guestpass,
                                              }
                                 })
                return messages
                
            except NoSuchElementException, ex:
                if count >= tries:
                    if self.browser.find_element_by_id('tip'):
                        errmsg = self.browser.find_element_by_id('tip').text
                    
                    messages.update({
                                     'generate': {
                                                  'status': False,
                                                  'message': errmsg+","+ex.message,
                                                  }
                                     })
            
        return messages
            
    def generate_one_guestpass_until_success(self,name,email,mobile,zd_ip='192.168.128.2'):
       
        
        while True:
            try:
                opener = FancyURLopener()
                req_data = '<ajax-request name="%s" email="%s" mobile="+86%s" sponsor="" updater="wlan-getter.1414734123296.9607" DECRYPT_X="true"/>'%(name,email,mobile)
                regist_url = 'http://%s/selfguestpass/_userRegistration.jsp'%zd_ip
                res = opener.open(regist_url,req_data).read()
                if "Email already exist" in res:
                    #print "%s already exist!"%name
                    return "EXIST"
                if "Maximum User Reached" in res:
                    print "Maximum User Reached. %s"%name
                    return "MAX"
            except Exception,e:
                print "Exception,[%s]"%e.message
                return False
    
    
    def generate_multiple_guestpass(self,start_time,start_num=1,zd_ip='192.168.128.2',target_num = 1000,timeout=TIMEOUT,):
        
        for i in range(start_num,1+target_num):
            if i<10000 and (time.time() - start_time) > timeout:
                return i
            name = "user_%s"%i
            email = name+"@test.com"
            mobile = 13900139000+i
            res = False
            res = self.generate_one_guestpass_until_success(name,email,mobile,zd_ip)
            if not res:
                print "Creating guestpass for %s failed."%name
                return i
            if res == "MAX":
                return "MAX"

        return 'Success'   
        

    def auth(self):
        super(SelfServiceGuestAuth, self).auth()

        if self.is_client_authorized():
            return True

        try:
            self.browser.get(self.params['dest_url'])
            self.browser.find_element_by_xpath(self.locators_self_service['portal_page_title'])
            textbox = self.browser.find_element_by_xpath(self.locators_self_service['guestpass_textbox'])
            textbox.send_keys(self.params['guestpass'])
                  
            button = self.browser.find_element_by_xpath(self.locators_self_service['login_button'])
            button.click()
            
            if self.check_is_reach_max_device():
                if self.params['sta_mac']:
                    if self.select_device_access_internet(self.params['sta_mac']):
                        return True
                    else: 
                        return False
                else:    
                    return False
            
                
        
        except NoSuchElementException, ex:
            self.message = ex.message + " Maybe target url can not redirector."
            return False
        
        return True


    def deauth(self):
        '''
        '''
        return super(SelfServiceGuestAuth, self).deauth()


    def is_login_successful(self):
        '''
        '''
        try:
            login_failed_div = self.browser.find_element_by_xpath(
                self.locators['login_failed']
            )

            self.message = login_failed_div.text
            return False

        except NoSuchElementException:
            self.message = "Login is done."

        return True
                                       
   
    def self_service_is_login_successful(self):
        '''
        '''
        try:
            login_failed_div = self.browser.find_element_by_xpath(
                self.locators_self_service['login_failed']
            )
            
            self.message = login_failed_div.text
            return False

        except NoSuchElementException:
            self.message = "Login is done."

        return True
    
    
    def check_is_reach_max_device(self):
        try:
            reach_max_device = self.browser.find_element_by_xpath(
                self.locators_self_service['max_device_text']
            )

            self.message = reach_max_device.text
            return True

        except NoSuchElementException:
            self.message = "Login is done."

        return False

    def select_device_access_internet(self,sta_mac):
       
        try:
            onePC_xpath = self.locators_self_service['select_onePC_checkbox']%sta_mac
            select_onePC_checkbox = self.browser.find_element_by_xpath(onePC_xpath)
            select_onePC_checkbox.click()
            
            access_button = self.browser.find_element_by_xpath(self.locators_self_service['access_button'])
            access_button.click()
            
        except NoSuchElementException, ex:
            message = "select one pc access internet failed."
            self.message = ex.message + message
            return False
            
        return True
            
    


    def check_and_accept_tou_if_found(self):
        '''
        '''
        try:
            tou_button = self.browser.find_element_by_xpath(
                self.locators['tou_button']
            )
        except NoSuchElementException:
            tou_button = None

        if bool(tou_button) ^ bool(self.params.get('use_tou')):
            self.message = \
                "TOU config and TOU page mismatched. "\
                "Either TOU is set but TOU page is not found, OR "\
                "TOU page is found while TOU is not set. "\
                "Please make sure tou_button XPath is correct."
            return False

        if tou_button:
            print "click tou_button"
            import time
            time.sleep(10)
            tou_button.click()
            self.message = "TOU has been accepted."

            return True

        if not self.params.get('use_tou'):
            self.message = "No TOU configured."

            return True


    def click_to_follow_redirect_url(self):
        '''
        '''
        try:
            redir_button = self.browser.find_element_by_xpath(
                self.locators['redirect_url']
            )

        except NoSuchElementException, ex:
            redir_button = False
            self.message = \
                "No redirect url was found. "\
                "Please make sure redirect_url XPath is correct."
            return False

        try:
            redir_button.click()
            self.message = "The redirect url was clicked."
            return True

        except Exception, ex:
            self.message = ex.message
            return False
        
    def check_element_is_exist(self,element,key='xpath'):
        try:
            if key is 'xpath':
                xpath_ret = self.browser.find_element_by_xpath(element)
                if xpath_ret:
                    return True
            elif key is 'id':
                id_ret = self.browser.find_element_by_id(element)
                if id_ret:
                    return True
            else:
                return False
            
        except:
            return False
        
        return False
        
   
    
    def wait_element_appear(self,element,key='xpath',timeout=3,base_timeout=1):
         
        while timeout < 20:
                time.sleep(timeout)
                print "wait %s second..."%timeout
                if self.check_element_is_exist(element,key):
                    return True
                else:
                    timeout = timeout + base_timeout
        return False
    
    
    def wait_url_appear(self,xpath,url="http://172.16.10.252",timeout=3,base_timeout=1):
         
        while timeout < 20:
                time.sleep(timeout)
                print "wait %s second..."%timeout
                self.browser.get(url)
                if self.check_element_is_exist(xpath):
                    return True
                else:
                    timeout = timeout + base_timeout
        return False
            
            
            
            
            
            
            

