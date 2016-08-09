import os
import time

from RuckusAutoTest.common.ProcessMgmt import createProcess
from RuckusAutoTest.common.DialogHandler import DialogManager, BaseDialog
from RuckusAutoTest.common.SeleniumClient import SeleniumClient
import RuckusAutoTest.common.Ratutils as RU

class SeleniumManager:
    """
    Provides functions to manage selenium server and client(s):
      - Loads server and starts clients
      - Kills server and stops clients
      - Closes all the remaining browsers after clients are stopped
    """
    def __init__(self, port = 4444):
        """ Start the selenium server on the specified port (default is 4444) """
        class_dir = os.path.join(os.path.dirname(__file__))
        (self.cmd, self.port) = RU.get_selenium_cmdline(class_dir,port=port)
        self.server = None

        self.clients = [] # a list of clients
        self._load_server() # starting the server now!


    def __del__(self):
        try: self.shutdown()
        except: pass


    def create_client(self, browser_type, url):
        """
        Input:
        - browser_type: now only two types of browsers are supported (ie and firefox)
        - url: the URL of the web application under test, derived from ip_addr
        """
        # should put the retrying code here (in case, starting IE browser)
        # but the code only restart the client
        client = SeleniumClient("localhost", self.port, browser_type, url)

        # NOTE:
        #   don't start the client now, let the WebUI.start() do this on demand.
        #self.start_client(client)

        self.clients.append(client) # add this client to the list

        return client


    def destroy_client(self, client):
        #print client
        for c in self.clients:
            if c == client:
                #print c
                try: client.stop()
                except: pass
                self.clients.remove(client)
                return True
        return False


    def to_url(self, ip_addr, https = True):
        """ util function
        Converting an IP address or an Web address to a full URL
        Examples:
        - to_url('192.168.0.2') will return        'https://192.168.0.2'
        - to_url('192.168.0.2', False) will return 'http://192.168.0.2'
        - to_url('www.google.com') will return     'https://www.google.com'
        """
        return ('https://' if https else 'http://') + ip_addr


    def shutdown(self):
        """
        Destroy all active clients and kill the server
        """

        # destroy all active clients
        for c in self.clients:
            try:
                c.stop()
            except:
                pass

        self.clients = []
        self.kill_server()


    def kill_server(self):
        """
        Kill selenium server
        There is another way to do the same job is used the selenium.shut_down_selenium_server()
        """
        if self.server:
            self.server.kill()
            self.server = None


    def _load_server(self):
        """ Load selenium server """
        self.kill_server()
        self.server = createProcess(self.cmd)
        time.sleep(5) # wait a bit for the server to load


    def stop_client(self, client):
        """
        Helper function for stopping the client
        These function should be put on the client itself. It is more reasonable.
        """
        client.stop()


    def start_client(self, client):
        """
        Helper function for starting the client
        These function should be put on the client itself. It is more reasonable.
        """
        try:
            client.start()

        except:
            return False

        self.start_dlg_manager(client.browser_type)

        client.open(client.url)
        client.wait_for_page_to_load()
        time.sleep(2)

        # These lines is for handling IE7 when accessing an unstrusted page
        if client.browser_type == 'ie' and \
           client.is_text_present("We recommend that you close this webpage"):
            client.click("overridelink")

        self.shutdown_dlg_manager()

        return True


    def start_dlg_manager(self, browser_type = 'firefox', dlg_cfg_list = []):
        '''
        '''
        if not dlg_cfg_list:
            dlg_cfg_list = self._get_default_dlg_list(browser_type)

        self.dlg_manager = DialogManager()

        for dlg_cfg in dlg_cfg_list:
            self.dlg_manager.add_dialog(
                BaseDialog(dlg_cfg['title'], dlg_cfg['text'],
                           dlg_cfg['button_name'], dlg_cfg['key_string'],
                           )
            )

        self.dlg_manager.start()


    def shutdown_dlg_manager(self):
        '''
        '''
        # Kill the dialog manager
        self.dlg_manager.shutdown()


    def _get_default_dlg_list(self, browser_type):
        '''
        '''
        dlg_cfg_list = []

        # IE browser dialogs
        if 'ie' == browser_type:
            dlg_cfg_list.append(
                {'title': 'Security Alert',
                 'text': 'You are about to view pages over a secure',
                 'button_name': 'OK',
                 'key_string': '',
                 }
            )
            dlg_cfg_list.append(
                {'title': 'Security Alert',
                 'text': 'The security certificate was issued by a company',
                 'button_name': '&Yes',
                 'key_string': '',
                 }
            )

        # Firefox browser dialogs
        elif 'firefox' == browser_type:
            dlg_cfg_list.append(
                {'title': 'Website Certified by an Unknown Authority',
                 'text': '',
                 'button_name': '',
                 'key_string': '{ENTER}',
                 }
            )
            dlg_cfg_list.append(
                {'title': 'Security Error: Domain Name Mismatch',
                 'text': '',
                 'button_name': '',
                 'key_string': '{TAB}{TAB}{ENTER}',
                 }
            )
            dlg_cfg_list.append(
                {'title': 'Add-ons',
                 'text': '',
                 'button_name': '',
                 'key_string': '{ESC}',                 
                 }
            )

        return dlg_cfg_list

