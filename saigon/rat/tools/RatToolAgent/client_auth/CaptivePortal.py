'''
'''
import utils

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import socket
import time


class CaptivePortal(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.browser = None
        self.params = {}

        self.message = ""
        self.__is_authorized = False


    def auth(self):
        '''
        '''
        self.verify_client_authorized()


    def deauth(self):
        '''
        '''
        pass


    def set_browser(self, browser):
        '''
        '''
        self.browser = browser


    def set_params(self, **kwargs):
        '''
        '''
        self.params.update(kwargs)


    def set_client_authorized(self, value):
        self.__is_authorized = value


    def is_client_authorized(self):
        '''
        '''
        return self.__is_authorized


    def verify_client_authorized(self, timeout = 6):
        '''
        '''
        default = socket.getdefaulttimeout()
        try:
        
            socket.setdefaulttimeout(60)
            self.browser.get(self.params['dest_url'])
        finally:
            socket.setdefaulttimeout(default)
            
        # in case of redirection, we need to wait for it to complete
        time.sleep(timeout)

        # then get the page source
        data = self.browser.page_source

        # and check if the expected data exists
        if self.params['expected_data'] in data:
            self.set_client_authorized(True)


    def is_redirect_url_correct(self):
        '''
        '''
        s_time = time.time()
        #@author: yuyanan @since: 2014-10-31 @change: 9.9sslldapnewfeature: adapt https redirector http
        redirect_url = self.params.get('redirect_url')
        index1 = redirect_url.find(':')
        new_redirector = redirect_url[index1:-1]
        current_url = self.browser.current_url
        index2 = current_url.find(':')
        new_current = current_url[index2:-1]    
        while time.time() - s_time < 30:
            if self.params.get('redirect_url') == self.browser.current_url or new_redirector ==new_current :
                self.message = "The redirect url is correct."
                return True
            else:
                time.sleep(2)

        self.message = "No redirect url configured. Or it[%s] is not as expected[%s]." % (self.browser.current_url, self.params.get('redirect_url'))
        return False


    def download_file(self):
        '''
        '''
        self.browser.get(self.params['validation_url'])
        if self.browser.title != self.params['page_title']:
            self.message = "The validation page was not found."
            return False

        try:
            link = self.browser.find_element_by_xpath(
                self.params['download_loc']
            )

        except NoSuchElementException, ex:
            self.message = \
                "Download location was not found. "\
                "Please make sure download_loc XPath is correct."
            return False

        try:
            link.click()
            file_path = utils.download_file_firefox(self.params['file_name'])
            self.message = file_path
            return True

        except Exception, ex:
            self.message = ex.message
            return False

