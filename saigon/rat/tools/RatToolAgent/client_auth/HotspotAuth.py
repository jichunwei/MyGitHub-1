'''
'''
from selenium.common.exceptions import NoSuchElementException

from client_auth.CaptivePortal import CaptivePortal


class HotspotAuth(CaptivePortal):
    '''
    classdocs
    '''

    locators = {
        'username_textbox': r"//input[@name='username']",
        'password_textbox': r"//input[@name='password']",
        'login_button': r"//input[@type='submit']",
    }


    def __init__(self):
        '''
        Constructor
        '''
        super(HotspotAuth, self).__init__()


    def auth(self):
        '''
        '''
        super(HotspotAuth, self).auth()

        if self.is_client_authorized():
            return

        self.browser.get(self.params['dest_url'])

        try:
            textbox = self.browser.find_element_by_xpath(
                self.locators['username_textbox']
            )
            textbox.send_keys(self.params['username'])

            textbox = self.browser.find_element_by_xpath(
                self.locators['password_textbox']
            )
            textbox.send_keys(self.params['password'])
            #Updated by chris@20130906, bug fix, not just do submit action, do click first and then call click funciton for set value purpose.
            login_btn = self.browser.find_element_by_xpath(self.locators['login_button'])
            login_btn.click()
        except NoSuchElementException, ex:
            self.message = ex.message
            return False

        #@author: anzuo, @change: wait "It works", max timeout is 25 sec, @since: 20140703
        import time
        timeout = 3
        base_timeout = 5
        while timeout < 25:
            time.sleep(timeout)
            super(HotspotAuth, self).auth()
        
            if self.is_client_authorized():
                return True
            else:
                timeout = timeout + base_timeout
        
        return False


    def deauth(self):
        '''
        '''
        return super(HotspotAuth, self).deauth()


    def is_login_successful(self):
        '''
        '''
        try:
            textbox = self.browser.find_element_by_xpath(
                self.locators['username_textbox']
            )

            self.message = \
                "It was redirected to login page after submitting username and password. " \
                "Login credentials may not correct."
            return False

        except NoSuchElementException, ex:
            self.message = "Login is done."

        return True

