# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
This is the base class for all Ruckus WebUI component
Please refer to the APWebUI.py for usage demonstration
"""
"""
The framework for loading resources is written on base class which will be available on concrete classes.

The idea here is that every concrete class inherits the resources from its fore-father classes
and it can override some or have its own resources.

Since each resource is a big dictionary so load it once for each class and share it among the instances.
Every new resource type should be added into the internal variable 'resource' of load_resource().

ENHANCEMENT:
In the future, this should be removed by enhancing the getting resource list from __import__
via using the dir() function, like:
    >>> x = __import__('RuckusAutoTest.components.experiment.BResource', fromlist=[''])
    >>> dir(x)
    ['Constants', 'Locators', '__builtins__', '__doc__', '__file__', '__name__']
  + just ignore __x__ items
"""
import time
import logging

from RuckusAutoTest.common.Ratutils import ping, is_ipv6_addr
from RuckusAutoTest.components.lib import FeatureUpdater as ftup


class WebUI:
    """ Static Properties
    These static properties are needed to be overridden in every single class.

    resource_file: is the resource file location, set it to None where there is no resource file
    resource:     is the place holder for loaded resource data, this must be initialized as None
    """
    resource_file = None
    resource = None


    @classmethod
    def _load_resource(cls, resource_file):
        """ Class method (static method)
        This function is a helper function for load_resource, this will return an import of
        the resource file.
        """
        return __import__(resource_file, fromlist = [''])


    @classmethod
    def _construct_locators(cls, locators, self_text = ''):
        """
        Recursive function for constructing all the locators
        Treat the 'self' node as a regular one (not a dict)
        """
        for k in locators.keys():
            if isinstance(locators[k], dict):
                if not locators[k].has_key('self'):
                    raise Exception('%s locator lacks "self" attribute' % k)

                # regular node: recursively call this function
                locators[k]['self'] = self_text + locators[k]['self']
                cls._construct_locators(locators[k], locators[k]['self'])
            else:
                # leaf node: add prefix only
                if k != 'self':
                    if not isinstance(locators[k], int):
                        locators[k] = self_text + locators[k]


    @classmethod
    def _flatten_locators(cls, root, first_level_key, locators):
        """
        The flatten Locators table is much helpful than a tree
        """
        for k, i in locators.iteritems():
            new_k = first_level_key + '_' + k
            if new_k in root:
                raise Exception('Key "%s" is not unique' % new_k)

            if isinstance(i, dict):
                # this is a dictionary so create an item for this
                # with the content in 'self'
                # and recursively flatten it
                root[new_k] = i['self']
                cls._flatten_locators(root, first_level_key, i)
            else:
                # since 'self' is processed on dictionary case
                # ignore it
                if k != 'self':
                    root[new_k] = i


    @classmethod
    def flatten_locators(cls, locators):
        flatten_locs = {}
        for k, i in locators.iteritems():
            if isinstance(i, dict):
                # this is dictionary
                cls._flatten_locators(flatten_locs, k, i)
            else:
                # normal item, just add it in
                if k != 'self':
                    flatten_locs[k] = i

        return flatten_locs


    @classmethod
    def load_resource(cls):
        """
        Load the resource file for this class, the resource will be stored in 'resource' property
        """
        import copy # for deep-copying the resource dictionary

        if cls.resource == None:
            resource = {'OrgLocators': {}, 'Constants': {}}
            # mapping from real resource keys to the internal resource keys
            # resource is loaded according to that maps
            resource_map = {'Locators': 'OrgLocators', 'Constants': 'Constants'}

            # if this is not the base class then call the load_resource() of father class
            # this part will be recursively called up to the base class load_resource() function
            # ASSUMPTION: single inheritance
            if len(cls.__bases__) != 0:
                cls.__bases__[0].load_resource() # call the father class static method
                resource = copy.deepcopy(cls.__bases__[0].resource)

            # if this class has resource_file then load and add/override the base class resource
            if cls.resource_file != None:
                imported_resource = cls._load_resource(cls.resource_file)

                for key in resource_map.keys():
                    if key in dir(imported_resource):
                        resource[resource_map[key]].update(imported_resource.__dict__[key])

            # clone the original Locators, construct and flatten locators
            tmp_locs = copy.deepcopy(resource['OrgLocators'])
            cls._construct_locators(tmp_locs)
            resource['Locators'] = cls.flatten_locators(tmp_locs)

            del tmp_locs

            # finally, update the resource static property of the class
            cls.resource = resource


    def __init__(self, selenium_mgr, browser_type, ip_addr,
                 selenium = None, https = True):
        self.browser_type = browser_type
        self.ip_addr = ip_addr
        self.selenium_mgr = selenium_mgr

        # Creating an instance of SeleniumClient
        # Or get the passed-in selenium
        if selenium == None:
            ip_addr_new = ip_addr
            
            #For ipv6, we need to add [], e.g. [2020:db8:1::2].
            if is_ipv6_addr(ip_addr):
                ip_addr_new = '[%s]' % ip_addr
            else:
                ip_addr_new = ip_addr
            
            self.selenium = selenium_mgr.create_client(
                browser_type, selenium_mgr.to_url(ip_addr_new, https)
            )
        else:
            self.selenium = selenium

        self.started = False # is this WebUI Selenium Client started yet?

        # Constants
        self.LOGIN_PAGE = -1
        self.NOMENU = -1 # in Dashboard, there is no menu
        self.HOME_PAGE = 0  # for Ruckus devices, it is usually the Dashboard
        self.HOME_PAGE_MENU = self.NOMENU

        self.current_tab = self.LOGIN_PAGE
        self.current_menu = self.NOMENU

        self.load_resource() # loading the resource
        self.info = self.resource['Locators']
        self.const = self.resource['Constants']
        self.s = self.selenium
        self._init_navigation_map()

        # the below attributes are needed to be overrided by concrete class
        self.username_loc = None
        self.password_loc = None

        self.login_loc = None
        self.logout_loc = None

        # register itself to Feature Updater
        ftup.FeatureUpdater.register(self)


    def __del__(self):
        """ Destructor
        Clean up the selenium client
        """
        #print self.selenium_mgr, self.selenium
        if self.selenium_mgr:
            # no need to logout here, self.stop() handles this
            self.selenium_mgr.destroy_client(self.selenium)
    
    def wait_login_page_load(self, timeout = 30, interval = 5):
        timepassed = 0
        s = self.selenium
        while timepassed <= timeout:
            if s.is_element_present(self.username_loc) and s.is_element_present(self.password_loc):
                return
            else:
                timepassed += interval
                self.refresh()
                time.sleep(interval)
        
        msg = "login page cannot load in %s seconds" % timeout
        logging.error(msg)
        raise Exception(msg)

    def refresh(self):
        s = self.selenium
        #Chico@2014-05-29, avoiding ocassionally popped login failed window. ZF-8295.
        if not s.is_element_present('//div[@id="loginfailed"]',1):
            try:
                s.refresh()
                time.sleep(2)
            except:
                pass
        #Chico@2014-05-29, avoiding ocassionally popped login failed window. ZF-8295.

    def login(self, force = False):
        """
        Login to WebUI

        NOTE:
        login() and logout()
        You don't need to call these functions explicitly, because it is called by start()/stop(),
        just do this in some special cases, especially in force cases

        Input:
        - force: in some cases, the webUI is timed-out, this helps re-login
        """
        s = self.selenium
        
        self.refresh()
            
        if self.is_logged_in():
            if not force:
                return
            else:
                self.logout()
        
        self.wait_login_page_load()

        s.type_text(self.username_loc, self.username)
        s.type_text(self.password_loc, self.password)
        time.sleep(.2)

        s.click(self.login_loc)
        s.wait_for_page_to_load()

        self.current_tab = self.HOME_PAGE
        self.current_menu = self.HOME_PAGE_MENU


    def update_location(self, tab, menu):
        '''
        . supports updating the current location of navigation
        '''
        self.current_tab = tab
        self.current_menu = menu


    def is_logged_in(self):
        """
        Return True if the webUI is logged in.
        The detection is based on the logout locator

        This function should be internal or
        checking whether selenium started or not before accessing it
        """
        self.refresh()
        
        s = self.selenium
        if s.is_element_present(self.username_loc,timeout =0.1) and s.is_element_present(self.password_loc,timeout =0.1):
            logging.info("zd web is not login, because username and password xpath are present")
            return False

        ret = s.is_element_present(self.logout_loc, 2)
        if not ret:
            logging.info("zd web is not login, because logout xpath is not present")
        return ret


    def logout(self):
        """
        Logout from the WebUI
        """
        s = self.selenium

        if self.current_tab != self.LOGIN_PAGE:
            self.current_tab = self.LOGIN_PAGE
            self.current_menu = self.NOMENU
            try:
                s.safe_click(self.logout_loc)
            except:
                pass # can't click here means already logged out
#            s.wait_for_page_to_load()


    def _init_navigation_map(self):
        '''
        . must be overrided on concrete class to provide navigation mapping
        '''
        pass


    def re_navigate(self):
        '''
        . force to renavigate to the current page
        '''
        return self.navigate_to(self.current_tab,
                                self.current_menu,
                                force = True)


    def navigate_to(self, tab, menu, loading_time = 1, timeout = 10, force = False):
        """
        Navigate to an specific page based on Tab and Menu indexes

        Input:
        - tab:     a tab on Web UI
        - menu:    a left-side menu item in Web UI
                   in Dashboard case, menu is self.NOMENU
        - loading_time: is the time waiting for AJAX content, in seconds
        - timeout:
        - force:   force go to the current page again

        Output:
        - none

        Usage:
            If we want to navigate to the item WLANs in the Configure page, we can do as below:
              self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS)
            In the special case the tab has no menu - DASHBOARD - then the menu_index is -1

            In case, there are timeouts, try to increase timeout:
              x.navigate_to(x.A, x.B, 3)
        """
        s = self.selenium
        end_time = time.time() + timeout
        menu_force = False
        tab_force = False

        if force:
            menu_force = False if menu == self.NOMENU else True
            tab_force = not menu_force

        while True:
            try:
                if not self.is_logged_in():
                    self.login()
                #edit by west.li,refresh the page if the required element not present
                #retry 5 rimes
                refresh_number=5
                wait_time = 10 # seconds
                if tab_force or tab != self.current_tab:
                    for refrest_time in range(1,refresh_number+1):
                        if s.is_element_present(tab):
                            break
                        else:
                            s.refresh()
                            time.sleep(wait_time)
                    s.click_and_wait(tab)
                    s.wait_for_page_to_load()
                    self.current_tab = tab

                if menu == self.NOMENU: # in DASHBOARD case
                    self.current_menu = self.NOMENU
                    break

                if menu_force or \
                   (menu != self.NOMENU and menu != self.current_menu):
                    #edit by west.li,refresh the page if the required element not present
                    #retry 5 rimes
                    for refrest_time in range(1,refresh_number+1):
                        if s.is_element_present(menu):
                            break
                        else:
                            s.refresh()
                            time.sleep(wait_time)
                    s.click_and_wait(menu)
                    s.wait_for_page_to_load()
                    self.current_menu = menu
                break
            except Exception:
                if time.time() < end_time:
                    time.sleep(0.25)
                    continue
                else:
                    raise
        # wait for the AJAX content to be loaded
        # even in the special case - the DASHBOARD
        time.sleep(loading_time)


    def start(self, tries = 3):
        """
        Wrapper functions for starting/stopping client browser
        """
        s = self.selenium
        count = 0
        while not self.started:
            count += 1
            try:
                self.selenium_mgr.start_client(self.selenium)
                s.wait_for_page_to_load()
                self.login()
                self.started = True

            except Exception:
                try:                    
                    self.destroy()
                    time.sleep(3)
                except Exception, e:
                    logging.debug(e.message)
                if count >= tries:
                    raise
                logging.debug('Try to start WebUI (%s) %s time(s)'
                              % (self.ip_addr, count))

        self.update_feature()


    def get_version(self):
        '''
        . this function is used by update_feature() so make sure it work with
          all device versions (even with a HACK!)
        '''
        raise Exception('Must be implemented by subclass')


    def update_feature(self):
        '''
        . this generic function should only be ran on subclasses
        . just some classes have the update ability, for those don't have this
          feature, just let get_version() return None
        '''
        ver = self.get_version()
        if ver:
            ftup.FeatureUpdater.notify(self, ver)


    def stop(self):
        """
        Wrapper functions for starting/stopping client browser
        """
        if self.started:
            try:
                #Sometime the AP cannot found the log out link, we will ignore
                # log out and stop selenium only in in this case
                self.logout(2)
            except:
                pass
            self.selenium_mgr.stop_client(self.selenium)
            self.started = False


    def destroy(self):
        """
        Wrapper functions for destroying client browser
        """
        #print 'start destroy'
        #if self.started:
        #print "Detroying this client %s" % self.selenium
        self.selenium_mgr.stop_client(self.selenium)
        self.selenium_mgr.destroy_client(self.selenium)
        self.started = False


    def get_cfg(self):
        '''
        This function is to ip_addr, username, password and return
        the config as a dictionary.
        NOTE: this is to bypass inconsistence between naming of
        password and password. Besides that, this would be better
        to get the config info from an internal function instead
        of accessing the config info directly
        '''
        return dict(ip_addr = self.ip_addr,
                    username = self.username,
                    password = self.password)


    def verify_component(self):
        '''
        . performing sanity check on the component
          . making sure the component is pingable
          . and its web UI is startable
        . if the web UI is not started by default, after checking this
          return it to the un-started state
        '''
        logging.info('Sanity check: Verify Test engine can ping %s WebUI (%s)'
                     % (self.__class__.__name__, self.ip_addr))

        if 'Timeout' in ping(self.ip_addr):
            raise Exception('Sanity check fails: cannot ping %s' % self.ip_addr)

        is_started = self.started
        if not self.started:
            self.start()

        try:
            self.login()
        except:
            raise Exception('Sanity check fails: cannot login %s'
                            % self.ip_addr)

        if not is_started:
            self.stop()
