'''
'''
import types

from selenium.common.exceptions import NoSuchElementException

from client_auth.CaptivePortal import CaptivePortal


class GuestAuth(CaptivePortal):
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


    def __init__(self):
        '''
        Constructor
        '''
        super(GuestAuth, self).__init__()


    def auth(self):
        '''
        '''
        super(GuestAuth, self).auth()

        if self.is_client_authorized():
            return True

        self.browser.get(self.params['dest_url'])
        
        #@author: Anzuo, @change: click "GUest Access" button firstly, zf-7389
        try:
            button = self.browser.find_element_by_xpath(
                self.locators['guestpass_button']
            )
            button.click()
        except NoSuchElementException, ex:
            self.message = ex.message

        if type(self.params['guestpass']) is types.DictType and self.params['guestpass'].get('authentication'):
            if self.params['guestpass']['authentication'] == 'No Authentication.':
                try:
                    tou_button = self.browser.find_element_by_xpath(self.locators['tou_button'])
                except NoSuchElementException, ex:
                    tou_button = None
                
                if tou_button:    
                    return True
                else:
                    return False

        try:
            textbox = self.browser.find_element_by_xpath(
                self.locators['guestpass_textbox']
            )
            textbox.send_keys(self.params['guestpass'])

            button = self.browser.find_element_by_xpath(
                self.locators['login_button']
            )
            button.click()
        except NoSuchElementException, ex:
            self.message = ex.message
            return False

        return True


    def deauth(self):
        '''
        '''
        return super(GuestAuth, self).deauth()


    def is_login_successful(self):
        '''
        '''
        try:
            login_failed_div = self.browser.find_element_by_xpath(
                self.locators['login_failed']
            )

            self.message = login_failed_div.text
            return False

        except NoSuchElementException, ex:
            self.message = "Login is done."

        return True


    def check_and_accept_tou_if_found(self):
        '''
        '''
        try:
            tou_button = self.browser.find_element_by_xpath(
                self.locators['tou_button']
            )
        except NoSuchElementException, ex:
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

