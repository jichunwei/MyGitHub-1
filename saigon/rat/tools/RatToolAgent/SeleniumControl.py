import threading
import time
from selenium import selenium
from pywinauto import application
from pywinauto import handleprops
from process import *

class Selenium:
    """ Provides functions to manage selenium server and client:

    - Loads server and starts client
    - Kills server and stops client
    - Closes all the remaining browsers after client stops
    """
    def __init__(self, browser_type, url):
        """ Class construction

        Input:
        - browser_type: now only two types of browsers are support (ie and firefox)
        - url: the URL of the web application under test
        """
        self.server = ""
        self.client = ""
        self.cmd = r"java -Djava.util.logging.config.file=rat-configuration.properties -jar selenium-server.jar -multiwindow"
        #self.ip_addr = ip_addr
        self.url = url

        # Define browser types
        if browser_type == "ie":
            browser_type = "*iehta"
        elif browser_type == "firefox":
            browser_type = "*chrome"
        else:
            browser_type = "*iehta"

        self.browser_type = browser_type

        # Start selenium client
        self.client = selenium("localhost", 4444, self.browser_type, self.url)

    def getClient(self):
        """ Return the client instance"""
        return self.client

    def _loadServer(self):
        """ Load selenium server

        This method is used by loadServerClient(), and is the private method
        """
        self.killServer()
        self.server = createProcess(self.cmd)
        return ["passed", "Load selenium server successfully"]

    def killServer(self):
        """ Kill selenium server"""
        if self.server:
            self.server.kill()
            self.server = ""
        return ["ok","Kill selenium server successfully"]

    def closeAllBrowsers(self):
        """ Close all IE browsers after the test script finished running.

        Sometimes Selenium client stops working but cannot close all the browsers that it has opened before
        - dlg_handle_list: find all IE browsers that are not closed
        after Test case finished.
        - dlg: connect to the browser with handle "handle_id"
        """
        # Stop selenium client
        self.client.stop()

        app = application.Application()

        # Find all remaining browsers
        dlg_handle_list = application.findwindows.find_windows \
                    (title_re = ".*Microsoft Internet Explorer$")
        try:
            # If one or more windows are found (stored in the dlg_handle_list),
            # connect to each of them and send Alt+F4 to close it(them)
            if len(dlg_handle_list) > 0 :
                for handle_id in dlg_handle_list:
                    dlg = app.connect_(handle = handle_id)

                    window_id = dlg.window_()

                    window_id.TypeKeys("%{F4}")
                    time.sleep(1)
        except:
            return ["error","Can not remove browser"]
        return ["ok","Remove browsers successfully"]

    def _startClient(self):
        """ Start selenium client

        This method is used by loadServerClient(), and is a private method
        """
        self.client.start()
        self.client.open(self.url)
        time.sleep(3)

        return ["ok", "Start client successfully"]

    def loadSelenium(self):
        """ Load selenium server and client. If the client fails to load then re-load server and client."""
        i = 20

        # If the selenium client fails to start, restart it again.
        while i > 0:
            self._loadServer()
            time.sleep(1)
            error_code, error_msg = self._startClient()
            if error_code == "ok":
                break
            i = i - 1
            time.sleep(2)

        if i == 0 :
            print "Cannot load selenium properly"
            return
