'''
'''
CONST_BROWSERS = {
    0: "firefox",
    1: "ie",
    2: "chrome",
    3: "remote",
}

BROWSER_ATTRS = {
    CONST_BROWSERS[0]: {
        'firefox_profile': None,
        'firefox_binary': None,
    },
    CONST_BROWSERS[1]: {
        'port': 0,
    },
    CONST_BROWSERS[2]: {
        'executable_path': "chromedriver",
        'port': 0,
    },
    CONST_BROWSERS[3]: {
        'command_executor': "http://127.0.0.1:4444/wd/hub",
        'desired_capabilities': None,
        'browser_profile': None,
    },
}

class BrowserAgent(object):
    '''
    '''
    browsers = {}
    current_id = 0


    def __init__(self):
        '''
        Constructor
        '''


    def init_browser(self, browser = None, timeout = 30, **kwargs):
        '''
        '''
        if browser not in CONST_BROWSERS.values():
            raise Exception(
                "The %s browser is invalid or currently not supported." %
                browser
            )

        BrowserAgent.current_id += 1
        browser_id = BrowserAgent.current_id

        BrowserAgent.browsers.update({
            browser_id: {
                'name': browser,
                'ins': None,
            },
        })

        if kwargs.has_key('timeout'):
            kwargs.pop('timeout')

        for k in BROWSER_ATTRS[browser]:
            if kwargs.has_key(k):
                BROWSER_ATTRS[browser].update({k: kwargs[k]})

        # Chrome does not have the timeout attribute
        if browser != CONST_BROWSERS[2]:
            BROWSER_ATTRS[browser].update({'timeout': timeout})

        # For Firefox, we may need to setup firefox_profile and firefox_binary
        # if these attributes are provided
        if browser == CONST_BROWSERS[0]:
            self._init_firefox(browser_id)

        return browser_id

        # DONE setting up!!
        # The launch_browser() will be called later to launch the browser


    def launch_browser(self, browser_id = 0):
        '''
        '''
        if not BrowserAgent.browsers.get(browser_id):
            raise Exception(
                "This browser id %s has not been initialized yet." %
                browser_id
            )        

        browser = BrowserAgent.browsers[browser_id]['name']

        WebDriver = __import__(
            "selenium.webdriver.%s.webdriver" % browser,
            fromlist = ['']
        ).__dict__['WebDriver']

        browser_ins = WebDriver(**BROWSER_ATTRS[browser])
        BrowserAgent.browsers[browser_id].update({'ins': browser_ins})

        return browser_ins


    def get_browser(self, browser_id = 0):
        '''
        '''
        if BrowserAgent.browsers.get(browser_id):
            return BrowserAgent.browsers[browser_id]['ins']

        return None


    def close_browser(self, browser_id = 0):
        '''
        '''
        try:
            browser_ins = self.get_browser(browser_id)
            
            if browser_ins:
                browser_ins.quit()
                del browser_ins
                BrowserAgent.browsers[browser_id]['ins'] = None
                #browser_dict = BrowserAgent.browsers.pop(browser_id)                
                #del browser_dict

        except Exception, ex:
            print(ex.message)


    def _init_firefox(self, browser_id = 0):
        '''
        '''
        browser = BrowserAgent.browsers[browser_id]['name']

        firefox = __import__(
            "selenium.webdriver.%s" % browser,
            fromlist = ['']
        )

        firefox_binary = firefox.firefox_binary.FirefoxBinary(
            BROWSER_ATTRS[browser]['firefox_binary']
        )
        firefox_profile = firefox.firefox_profile.FirefoxProfile(
            BROWSER_ATTRS[browser]['firefox_profile']
        )
        
        #Chico, 2015-8-13, change the default download path to 'Desktop'
        firefox_profile.set_preference("browser.download.folderList", 0)
        #Chico, 2015-8-13, change the default download path to 'Desktop'
            
        #@author: yuyanan @since: 2015-3-27 @change:resolve after upgrade firefox and selenium
        #BROWSER_ATTRS[browser].update({
        #    'firefox_binary': firefox_binary,
        #    'firefox_profile': firefox_profile,
        #})


if __name__ == "__main__":
    agent = BrowserAgent()

    print("Starting Firefox...")
    browser_id1 = agent.init_browser("firefox")
    browser1 = agent.launch_browser(browser_id1)

    print("Starting Internet Explorer...")
    browser_id2 = agent.init_browser("ie")
    browser2 = agent.launch_browser(browser_id2)

    print("Starting Google Chrome...")
    browser_id3 = agent.init_browser("chrome")
    browser3 = agent.launch_browser(browser_id3)

    print("Close browser2 - Internet Explorer")
    agent.close_browser(browser_id2)

    print("Close browser3 - Google Chrome")
    agent.close_browser(browser_id3)

    print("Close browser1 - Firefox")
    agent.close_browser(browser_id1)

    print("Done")


