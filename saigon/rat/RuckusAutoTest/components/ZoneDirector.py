# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
The ZoneDirector class provides functions to manipulate on the web UI of a Zone Director.
This class inherits the base class DUT, which provides an standard interface for users.
All the methods in the class DUT are overridden in this class
by public methods basing on the features of Zone Director.
"""

import re
import logging
import random
import time
import os

from RuckusAutoTest.components.lib.zd import alarm_setting_zd as asz
from pprint import pformat
from tarfile import TarFile

from RuckusAutoTest.components.DUT import DUT
from RuckusAutoTest.components.WebUI import WebUI
from RuckusAutoTest.common.DialogHandler import (
        DialogManager, BaseDialog, StandardDialog
)
from RuckusAutoTest.common.Ratutils import ping, is_ipv6_addr
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import ap_group
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl
from RuckusAutoTest.components.lib.zd import (
    widgets_zd as WGT,
    wlan_groups_zd as WGS,
    guest_access_zd as GA,
    mgmt_vlan_zd as MVLAN,
    hotspot_services_zd as WISPR,
    aps as APS,
    aaa_servers_zd as AAA,
    wlan_zd as WLAN,
    access_control_zd as AC,
    access_points_zd as AP,
    active_clients_zd as CAC,
    user as USER,
    rogue_devices_zd as ROGUE,
    wips_zd as WIPS,
)
from RuckusAutoTest.components.lib.zd.release_compare import older_than_release

AP_INFO_HDR_MAP = {
    'description': 'description',
    'devname': 'device_name',
    'ip': 'ip_addr',
    'ipv6': 'ipv6',
    'mac': 'mac',
    'mesh_mode': 'mesh_mode',
    'mgmt_vlan_id': 'vlan',
    'model': 'model',
    'num_sta': 'clients',
    'radio_channel': 'channel',
    'state': 'status'
}

ACTIVE_CLIENT_HDR_MAP = {
    #9.8:[u'mac', u'dvcinfo', u'hostname', u'user', u'role', u'ap', u'wlan', u'vlan', u'channel', u'radio_type_text', u'rssi', u'status', u'auth_method', u'action']
    'ap': 'apmac',
    'channel': 'channel',
    'user': 'ip',
    'role':'role',
    'mac': 'mac',
    #@author: Jane.Guo @since: 2013-09 adapt to 9.8
    #@zj 2013-12-4 ZF-6436 behavior change , "radio_type_text" ->"radio_type"
    'radio_type_text': 'radio',
    'rssi': 'signal',
    'status': 'status',
    'vlan': 'vlan',
    'wlan': 'wlan',
    'dvcinfo': 'ostype',
    'hostname': 'hostname',
}
DEFAULT_GUEST_ACCESS_NAME = 'Guest_Access_Default'

class ZoneDirector2(WebUI, DUT):
    resource_file = 'RuckusAutoTest.components.resources.ZDWebUIResource'
    resource = None

    # holds a list of XPath changes
    feature_update = __import__('RuckusAutoTest.components.resources.ZDFeatureUpdate',
                                fromlist = ['']).feature_update

    username = 'admin'
    password = 'admin'


    def __init__(self, selenium_mgr, browser_type, ip_addr, config, https = True):
        """
        The constructor of the class is reponsible for initializing variables, loading selenium.

        Input:
        - browser_type: only two types of browsers ('ie' and 'firefox') are supported now.
        - ip_addr: ip address of zone director.
        - username: username to login to ZD
        - password: password to login to ZD
        """
        self.config = config
        self.conf = dict(
            browser_type = 'firefox',
            ip_addr = '192.168.0.2',
            username = 'admin',
            password = 'admin',
            loadtime_login = 15500,
            loadtime_stepout = 5500,
            loadtime_open1 = 10500,
            loadtime_open2 = 30500,
            timeout = 17000,
            init = True,
            init_s = True,
            login_type = 0,
            debug = 0,
            shell_key = '!v54!',
        )
        self.conf.update(config)

        # init the farther class
        WebUI.__init__(self, selenium_mgr, browser_type, ip_addr, https = https)

        # Add new variable to make back compatible with ZD
        self.https = https
        # defining values for "abstract" attributes

        self.HOME_PAGE = self.DASHBOARD # = 0
        self.HOME_PAGE_MENU = self.NOMENU

        try:
            self.username = config['username']
            self.password = config['password']
            self.shell_key = self.conf['!v54!'] #shell_key

        except:
            pass

        self.info = self.resource['Locators']
        self.has_mgmt_vlan = False
        self.username_loc = self.info['LoginUsernameTxt']
        self.password_loc = self.info['LoginPasswordTxt']

        self.login_loc = self.info['LoginBtn']
        self.logout_loc = self.info['LogoutBtn']

        if self.conf['init']:
            self.initialize()
            
        #@author: Anzuo, @change: assign ip and mac address 
        self.ip_addr = self.conf.get("ip_addr")
        
        count = 3
        while count >0:
            self.mac_addr = self.get_mac_address()
            if self.mac_addr:
                self.eth_mac = self.mac_addr
                logging.info("zd[%s]'s eth_mac is %s"%(self.ip_addr,self.eth_mac))
                break
            else:
                count = count - 1
            
            if count == 0:
                raise Exception('cannot get zd mac address')


    def init_messages_bundled(self, cli = None):
        '''
        '''
        from RuckusAutoTest.components.Messages import Messages as messages

        if cli is not None:
            msg_file = '/bin/messages'
            self.messages = messages.load_zd_messages(cli, msg_file)

            msg_file = '/bin/messages.en_US'
            self.messages = messages.load_zd_messages(cli, msg_file)


    def navigate_to(self, tab_index , menu_index = 0, loading_time = 1, timeout = 10, force = False):
        return WebUI.navigate_to(self, tab_index, menu_index, loading_time, timeout, force)


    def start(self, tries = 3):
        '''
        .Adapter method for specific start procedure under ZoneDirector
        '''
        WebUI.start(self, tries)

        self.init_messages_bundled()


    def initialize(self):
        # my startup DEFAULT variables/values
        self.init_constants()
        #self.init_position()
        self.touch_page_load_time()
        
        ip_addr_str = str(self.get_cfg()['ip_addr'])
        
        #For ipv6, need to add [].
        if is_ipv6_addr(ip_addr_str):
            ip_addr_str = '[%s]' % ip_addr_str

        self.url = self.conf['url'] = "https://" + ip_addr_str 
        self.conf['url.login'] = "https://" + ip_addr_str + "/admin/login.jsp"
        self.conf['url.dashboard'] = "https://" + ip_addr_str + "/admin/dashboard.jsp"

        # PHANNT@20100318: to decrease timeout since the default value = 60 in SeleniumClient causes
        # the scripts to wait much time. Suggested value is 17, but if encountering issue,
        # we will increase it to 30.
        self.selenium.set_timeout(int(self.conf['timeout']) / 1000)

        self.s = self.selenium

        if self.conf['init_s']: # keep original behavior
            self.start()


    def _init_navigation_map(self):
        # Tabs
        self.DASHBOARD = self.info['loc_dashboard_anchor']
        self.MONITOR = self.info['loc_monitor_anchor']
        self.CONFIGURE = self.info['loc_configure_anchor']
        self.ADMIN = self.info['loc_admin_anchor']

        #only used in authorization cases
        self.DISABLED_CONFIGURE = self.info['disabled_cfg_span']

        # Monitor menu
        self.MONITOR_ACCESS_POINTS = self.info['loc_mon_access_points_span']
        self.MONITOR_MAP_VIEW = self.info['loc_mon_map_view_span']
        self.MONITOR_WLAN = self.info['loc_mon_wlan_span']
        self.MONITOR_CURRENTLY_ACTIVE_CLIENTS = self.info['loc_mon_currently_active_clients_span']
        self.MONITOR_CURRENTLY_ACTIVE_WIRED_CLIENTS = self.info['loc_mon_currently_active_wired_clients_span']
        self.MONITOR_GENERATED_PSK_CERTS = self.info['loc_mon_generated_psk_certs_span']
        self.MONITOR_GENERATED_GUESTPASSES = self.info['loc_mon_generated_guestpasses_span']
        self.MONITOR_ROGUE_DEVICES = self.info['loc_mon_rogue_devices_span']
        self.MONITOR_ALL_EVENTS_ACTIVITIES = self.info['loc_mon_all_events_activities_span']
        self.MONITOR_ALL_ALARMS = self.info['loc_mon_all_alarms_span']
        self.MONITOR_SYSTEM_INFO = self.info['loc_mon_system_info_span']
        self.MONITOR_REAL_TIME = self.info['loc_mon_real_time_monitor']

        # Configure menu
        self.CONFIGURE_SYSTEM = self.info['loc_cfg_system_span']
        self.CONFIGURE_WLANS = self.info['loc_cfg_wlans_span']
        self.CONFIGURE_ACCESS_POINT = self.info['loc_cfg_access_point_span']
        self.CONFIGURE_ACCESS_CONTROLS = self.info['loc_cfg_access_controls_span']
        self.CONFIGURE_MAPS = self.info['loc_cfg_maps_span']
        self.CONFIGURE_ROLES = self.info['loc_cfg_roles_span']
        self.CONFIGURE_USERS = self.info['loc_cfg_users_span']
        self.CONFIGURE_GUEST_ACCESS = self.info['loc_cfg_guest_access_span']
        self.CONFIGURE_AUTHENTICATION_SERVER = self.info['loc_cfg_authentication_servers_span']
        self.CONFIGURE_ALARM_SETTINGS = self.info['loc_cfg_alarm_settings_span']
        self.CONFIGURE_SERVICES = self.info['loc_cfg_services_span']
        self.CONFIGURE_MESH = self.info['loc_cfg_mesh_span']
        self.CONFIGURE_HOTSPOT_SERVICES = self.info['loc_cfg_hotspot_span']
        self.CONFIGURE_WIPS = self.info['loc_cfg_wips_span']
        self.CONFIGURE_CERTIFICATE = self.info['loc_cfg_cerificate_span']

        # Admin menu
        self.ADMIN_PREFERENCE = self.info['loc_admin_preference_span']
        self.ADMIN_BACKUP = self.info['loc_admin_backup_span']
        self.ADMIN_RESTART = self.info['loc_admin_restart_span']
        self.ADMIN_UPGRADE = self.info['loc_admin_upgrade_span']
        self.ADMIN_LICENSE = self.info['loc_admin_license_span']
        self.ADMIN_DIAGNOSTIC = self.info['loc_admin_diagnostic_span']
        self.ADMIN_REG = self.info['loc_admin_registration_span']
        self.ADMIN_SUPPORT = self.info['loc_admin_support_span']

    def init_constants(self):
        self.LOG_ALL = "high"
        self.LOG_CRITICAL_WARNING = "medium"
        self.LOG_CRITICAL_ONLY = "low"


    def cfg_wlan(self, wlan_cfg):
        """
        Configure a new wlan for Zone Director.

        Input: a dictionary, supplied in DUT.py
        Output: none
        """

        if wlan_cfg['auth'] == "PSK":
            auth = "open"

        else:
            auth = wlan_cfg['auth']

        auth_server = ""
        vlan_id = ""
        acl_name = ""
        uplink_rate_limit = ""
        downlink_rate_limit = ""
        use_web_auth = False
        use_hide_ssid = False
        use_guest_access = False
        use_client_isolation = False
        use_zero_it = False
        use_dynamic_psk = False
        do_tunnel = False

        if auth == "EAP":
            if wlan_cfg['use_radius']:
                auth_server = wlan_cfg['ras_addr']

        else:
            if wlan_cfg.has_key('use_web_auth'):
                if wlan_cfg['use_web_auth']:
                    use_web_auth = wlan_cfg['use_web_auth']
                    if wlan_cfg['ras_addr']:
                        auth_server = wlan_cfg['ras_addr']
                    elif wlan_cfg['ad_addr']:
                        auth_server = wlan_cfg['ad_addr']

        if wlan_cfg.has_key('use_guest_access'):
            use_guest_access = wlan_cfg['use_guest_access']

        if wlan_cfg.has_key('use_client_isolation'):
            use_client_isolation = wlan_cfg['use_client_isolation']

        if wlan_cfg.has_key('acl_name'):
            acl_name = wlan_cfg['acl_name']

        if wlan_cfg.has_key('use_hide_ssid'):
            use_hide_ssid = wlan_cfg['use_hide_ssid']

        if wlan_cfg.has_key('vlan_id'):
            vlan_id = wlan_cfg['vlan_id']

        if wlan_cfg.has_key('uplink_rate_limit'):
            uplink_rate_limit = wlan_cfg['uplink_rate_limit']
        if wlan_cfg.has_key('downlink_rate_limit'):
            downlink_rate_limit = wlan_cfg['downlink_rate_limit']

        if wlan_cfg.has_key('use_zero_it'):
            use_zero_it = wlan_cfg['use_zero_it']
            if wlan_cfg.has_key('use_dynamic_psk'):
                use_dynamic_psk = wlan_cfg['use_dynamic_psk']

        if wlan_cfg.has_key('do_tunnel'):
            do_tunnel = wlan_cfg['do_tunnel']

        try:
            #@author: Jane.Guo @since: 2013-10 adapt to 9.8 guest access improvement
            if use_guest_access == True:
                logging.info("Create default guest access profile")
                GA.create_default_guestaccess_policy(self)
                GA.remove_restricted_subnet_entry(self, 4)
                GA.remove_restricted_subnet_entry(self, 3)
                GA.remove_restricted_subnet_entry(self, 2)
                          
            self._create_wlan(wlan_cfg['ssid'], auth, wlan_cfg['encryption'],
                              wlan_cfg['wpa_ver'], wlan_cfg['key_string'],
                              wlan_cfg['key_index'], auth_server,
                              use_web_auth, use_guest_access, acl_name, use_hide_ssid,
                              vlan_id, uplink_rate_limit, downlink_rate_limit,
                              use_client_isolation, use_zero_it,
                              use_dynamic_psk, do_tunnel)
        except:
            raise


    def remove_wlan(self, wlan_cfg):
        """
        Remove a wlan out of the WLAN table.

        If that wlan uses Radius authentication server, remove that Authentication server
        If that wlan uses a local database account, remove that account off the User table

        Input: a dictionary, supplied in DUT.py
        Output: none
        """
        self._delete_wlan(wlan_cfg['ssid'])

        if wlan_cfg['auth'] == "EAP":
            if wlan_cfg['use_radius']:
                self._delete_radius_server(wlan_cfg['ras_addr'])

            else:
                self._delete_user(wlan_cfg['username'])


    def remove_all_wlan(self):
        """
        Remove all configured wlans out of the WLANs table
        """
        self._delete_all_wlan()


    def remove_all_wlan_group(self):
        '''
        This function is to remove all wlan group
        @TODO: this is just for quick development, will move to a better place later
        '''
        WGS.remove_wlan_groups(self)


    def get_wlan_list(self):
        """
        Return the wlan name list on the ZD
        """
        self.navigate_to(self.MONITOR, self.MONITOR_WLAN)

        i = 0
        wlan_list = []

        while True:
            a = self.info['loc_mon_wlan_name_cell']
            a = a.replace("$_$", str(i))

            if not self.s.is_element_present(a):
                break

            wlan_list.append(self.s.get_text(a))
            i += 1

        return wlan_list


    def remove_all_cfg(self, ap_mac_list = []):
        """
        Remove all configurations on the ZoneDirector (wlans, clients, authentication servers, users...)
        to prevent the duplication when creating new configurations about them.

        Input: none
        Output: none
        """
        self.set_system_name("Ruckus")
        self.set_guestpass_policy("Local Database")    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
        self._set_zero_it_cfg("Local Database")
        self._remove_all_generated_certs()
        self._remove_all_generated_psks()

        self.remove_all_active_clients()
        self.remove_all_acl_rules()
        self.remove_all_guestpasses()
        GA.remove_all_restricted_subnet_entries(self)
        GA.remove_all_restricted_subnet_entries_ipv6(self)
        self.remove_all_roles()
        self.remove_all_users()
        try:
            WGS.remove_wlan_groups(self, ap_mac_list)
        except:
            lib.zd.ap.assign_all_ap_to_default_wlan_group(self)
            WGS.remove_wlan_groups(self)
        self.remove_all_wlan()
        WISPR.remove_all_profiles(self)
        self.remove_all_auth_servers()


    def remove_all_cfg_v9(self, ap_mac_list = []):
        logging.info('remove all cfg in zd %s' % self.ip_addr)
        self.set_system_name("Ruckus")

        self.set_guestpass_policy("Local Database")    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226

        logging.info("Choose 'Local Database' for zero-it")
        self._set_zero_it_cfg("Local Database")

        logging.info("Remove all dynamic-certs out of the Generate Dynamic-Certs table")
        self._remove_all_generated_certs()

        logging.info("Remove all dynamic-PSKs out of the Generate Dynamic-PSKs table")
        self._remove_all_generated_psks()

        logging.info("Remove all active clients")
        self.remove_all_active_clients()

        logging.info("Remove all guest pass entries from the Generated Guest Passes table")
        self.remove_all_guestpasses()

        logging.info("Remove all guest ACL rules except the default rule")
        GA.remove_all_restricted_subnet_entries(self)
        GA.remove_all_restricted_subnet_entries_ipv6(self)

        logging.info("Remove all users from the Users table")
        USER.delete_all_users(self)

        logging.info("Remove all roles from the Roles table")
        self.remove_all_roles()
        
        logging.info("Remove all ap group from the ap group table")
        ap_group.delete_all_ap_group(self)

        try:
            logging.info("Remove all wlan groups from the WLAN Groups table")
            WGS.remove_wlan_groups(self, ap_mac_list)
        except:
            lib.zd.ap.assign_all_ap_to_default_wlan_group(self)
            WGS.remove_wlan_groups(self)

        logging.info("Remove all wlan from the WLANs table")
        WLAN.delete_all_wlans(self)

        logging.info("Remove all ACL rules from the Access Controls table")
        self.remove_all_acl_rules()

        logging.info("Remove all profiles from the Hotspot Services table")
        if WISPR.get_total_profiles(self) != '0':
            WISPR.remove_all_profiles(self)

        logging.info("Remove all AAA servers")
        self.remove_all_auth_servers()
        
        logging.info("Remove all mgmtacl")
        mgmt_ip_acl.delete_all_mgmtipacl(self)
        
        logging.info("Remove all maps")
        self.delete_all_maps()

    #Jacky.Luh update by 2012-06-26    
    def enable_web_auth_debug_comp(self):
        self.navigate_to(self.ADMIN, self.ADMIN_DIAGNOSTIC)
        self.s.click_if_not_checked("//input[@id='web-auth']")
        self.s.click_and_wait("//input[@id='apply-log']")
        
    #Jacky.Luh update by 2012-06-26    
    def disable_web_auth_debug_comp(self):
        self.navigate_to(self.ADMIN, self.ADMIN_DIAGNOSTIC)
        self.s.click_if_checked("//input[@id='web-auth']")
        self.s.click_and_wait("//input[@id='apply-log']")        

    #Jacky.Luh update by 2012-06-26
    def upgrade_sw(self, filename, force_upgrade = False, rm_data_files = False, 
                   build_version = None, factory = False, mesh_enabled = False):
        """
        Upgrade the Zone Director with the image specified by the filename.
        Before upgrading, untar the image file (.gz) to the appropriate format (.img)

        Input:
        - filename: Full path to the .gz or .img file
        Output: none
        """
        t0 = time.time()
        factory_id = False
        self.mesh_enabled = mesh_enabled
        (current_ver, base_build_ver, img_filename) = self._get_target_build_image(filename)
        if not force_upgrade and current_ver == base_build_ver:
            logging.info("No need to upgrade the Zone Director. Current version %s" % current_ver)
        else:
            logging.info("Current version %s" % current_ver)
            logging.info("Upgrade the Zone Director to version %s" % base_build_ver)
            img_filename = os.path.join(os.getcwd(), img_filename)
            factory_id = self._upgrade(img_filename, factory, build_version)

        if rm_data_files:
            if os.getcwd() in img_filename:
                os.remove(img_filename)
        elapsed = time.time() - t0

        return elapsed, factory_id


    #Jacky.Luh update by 2012-06-26
    def _get_target_build_image(self, filename):
        if '.img' in filename:
            if "\\" in filename:
                img_file_list = filename.split("\\")
                img_name = ''
                for img in img_file_list:
                    if '.img' in img:
                        img_name = img                                
            img_filename = filename
            base_build_ver = re.findall(r'^zd\d{1,4}k{0,1}\_(.*)\.{1}ap\_.*', img_name)
        else:
            logging.info("Target build image to upgrade is in gz file %s" % filename)
            build_number_re = ["([0-9]+)\.tar.gz", "build_no_(\d+)_"] # An Nguyen: fixed the build name parse issued
            for re_str in build_number_re:
                match_obj = re.search(re_str, filename)
                if match_obj:
                    break
            if not match_obj:
                raise Exception("Can not find any build number in the filename %s" % filename)
    
            build_number = match_obj.group(1)
    
            # Untar image file to the build directory
            tar_file = TarFile.open(filename, 'r:gz')
            file_string = ';'.join(tar_file.getnames())
    
            # begin with Odessa (7.0); version is prefix platform version 1k|3k
            pat_img = "zd(|\dk)_[0-9\.]+\.%s\.[ap_0-9\.]+\.img" % build_number
            match_obj = re.search(pat_img, file_string)
            if match_obj:
                img_filename = match_obj.group(0)
                try:
                    tar_file.extract(img_filename)
                except:
                    tar_file.extract("./%s" % img_filename)
    
            else:
                raise Exception("File .img not found")

        logging.info("Target build image for ZD to upgrade is %s" % img_filename)
        pat_ver = "(zd(|\d{1,4}k{0,1})_([0-9\.]+)).ap"
        match_obj = re.search(pat_ver, img_filename)
        if not match_obj:
            raise Exception("Can not find ZD image version in the filename %s" % img_filename)

        base_build_ver = unicode(match_obj.group(3))
        logging.info("Build image version %s" % base_build_ver)

        current_ver = unicode(self._get_version()['version'])

        return (current_ver, base_build_ver, img_filename)


    #Jacky.Luh update by 2012-06-26
    def wait_aps_join_in_zd(self, list_of_connected_aps = {}):
        logging.info("Verify all aps can be joined in ZD. This process maybe take some minutes. Please wait... ")
        ap_upgrade_timeout = 1800
        ap_upgrade_start_time = time.time()
        if list_of_connected_aps == {}:
            list_of_connected_aps = self.get_all_ap_info()
        for associated_ap in list_of_connected_aps:
            while(True):
                if (time.time() - ap_upgrade_start_time) > ap_upgrade_timeout:
                    raise Exception("Error: AP upgrading failed. Timeout")
                try:
                    time.sleep(10)
                    self.refresh()
                    if (self._get_ap_info(associated_ap['mac']))['status'].lower().startswith(u"connected"):
                        break
                except:
                    time.sleep(2)
                    pass    

    #Updated by cwang@20130509, remove postfix tag v5
    def set_ap_policy_approval(self, auto_approval = True, max_clients = 0, apgrp_name = 'System Default', ap_model = 'zf2741'):
        """
        Set the status of the approval policy checkbox button. It can be checked or unchecked.
        And set the maximum numbers of clients that an AP can handle
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_POINT, 1)
        approval = self.info['loc_cfg_appolicy_allow_all_checkbox']

        if auto_approval:
            if not self.s.is_checked(approval):
                self.s.click_and_wait(approval, 2)

        else:
            if self.s.is_checked(approval):
                self.s.click_and_wait(approval, 2)

        self.s.click_and_wait(self.info['loc_cfg_appolicy_apply_button'])

        if max_clients:
            ap_group.set_ap_model_max_client_by_name(self, apgrp_name, ap_model, max_clients)


    #Updated by cwang@20130529, remove tag v5
    def get_ap_policy_approval(self, apgrp_name = 'System Default', ap_model = 'zf7982'):
        """
        Get status of approval policy checkbox button to verify that whether it is checked or not,
        and get the maximum clients that an AP can handle
        Output: return a dictionary of two informations (the status of approval policy and max numbers of clients)
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_POINT)

        checkbox = self.info['loc_cfg_appolicy_allow_all_checkbox']
        approval = self.s.is_checked(checkbox)
        
        max_clients = ap_group.get_ap_model_max_client_by_name(self, apgrp_name, ap_model)
        return {'approval':approval, 'max_clients':max_clients}

    def allow_ap_joining(self, mac_addr):
        """
        WARNING: OBSOLETE, please use lib.zd.aps.allow_ap_joining_by_mac_addr()
        This function click allow buttion at Monitor/Access Points page to approve
        for the AP joined the ZD
        Input:
        - mac_addr: mac address of allowed AP
        """
        return APS.allow_ap_joining_by_mac_addr(self, mac_addr)


    def remove_approval_ap(self, mac_addr = ""):
        """
        Remove one AP or all APs out of the AccessPoints table
        Input:
        - mac_addr: mac address of the deleted AP. If mac_addr is null, it means all APs will be removed.
        """
        if mac_addr:
            time.sleep(50) # wait the target ap to be connected before test.
            self._delete_ap(mac_addr)

        else:
            self._delete_all_aps()


    def cfg_ntp(self, ntp_serv = ""):
        """
        Config the NTP options server for the Zone Director
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 1)

        self.s.click_if_not_checked(self.info['loc_cfg_system_time_ntp_checkbox'])
        if ntp_serv:
            self.s.type_text(self.info['loc_cfg_system_time_ntp_textbox'], ntp_serv)

        self.s.click_and_wait(self.info['loc_cfg_system_time_apply_button'], 3)

    def get_current_time(self, is_sync_with_pc_time = False):
        """
        This function is used to get system time of ZD
        Input:
        - is_sync_with_pc_time: if it's True, ZD will be synchronized with PC time before getting its system time
        Otherwise, just get system time on ZD
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)

        if is_sync_with_pc_time:
            self.s.click_and_wait(self.info['loc_cfg_system_time_sync_button'], 3)

        self.s.click_and_wait(self.info['loc_cfg_system_time_refresh_button'], 3)

        current_time = self.s.get_text(self.info['loc_cfg_system_time_curtime_textbox'])

        return current_time

    def get_ntp_cfg(self):
        """
        Get the current configuration of NTP server
        Input: none
        Output: return the name of the ntp server
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)

        if not self.s.is_element_present(self.info['loc_cfg_system_time_ntp_textbox']):
            raise Exception("Element %s not found" % self.info['loc_cfg_system_time_ntp_textbox'])
        time.sleep(2)
        ntp_conf = self.s.get_value(self.info['loc_cfg_system_time_ntp_textbox'])

        return ntp_conf


    def get_total_aps_num_from_monitor_tab(self, timeout = 150, is_refresh = True):
        """
        Get total number from monitor/access points page.
        """
        self.navigate_to(self.MONITOR, self.MONITOR_ACCESS_POINTS)
        locator = self.info['loc_mon_access_points_total_number_span']
        if self._wait_for_element(locator, timeout = timeout, is_refresh = is_refresh):
            #louis.lou@ruckuswireless.com, add timeout for scaling test loading the ap number
            time.sleep(10)
            return int(self._get_total_number(locator, 'apsummary'))
        else:
            raise Exception('Element[%s] not found' % locator)


    def get_total_aps_num_from_configure_tab(self, timeout = 150, is_refresh = True):
        """
        Get total number from configure/access points page.
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_POINT)
        locator = self.info['loc_cfg_ap_total_number_span']
        if self._wait_for_element(locator, timeout = timeout, is_refresh = is_refresh):
            #louis.lou@ruckuswireless.com, add timeout for scaling test loading the ap number
            time.sleep(10)
            return int(self._get_total_number(locator, "ap"))
        else:
            raise Exception('Element[%s] not found' % locator)


    def get_all_ap_info(self, mac_addr = ""):
        """
        WARNING: OBSOLETE
        . please use get_all_ap_briefs, get_ap_brief_by_mac_addr in lib.zd.aps

        Get information of one AP or all APs from the AP-Summary table
        Input:
        - mac_addr: mac address of particular AP. If this variable is not null, this function returns a
        dictionary containing  information of that AP. Otherwise, this function returns a list of dictionaries,
        in there, each dictionary contains information of each AP.
        """
        res = None
        if mac_addr:
            # PHANNT@20100526:
            # This is to provide compatibility to the old TCs code because it
            # will raise Exception: "No matched row found." when trying to get
            # a non-existent AP in the AP-Summary table.
            try:
                res = self._get_ap_info(mac_addr)

            except Exception, e:
                if 'No matched row found' in e.message:
                    return None

        else:
            res = self._get_all_ap_info()

        return res


    def get_all_ap_sym_dict(self):
        ap_sym_list = {}
        ap_id = 0
        for ap in self.sort_ap_by_model(self.get_all_ap_info()):
            ap_id += 1
            ap_sym_name = 'AP_%02d' % ap_id
            ap_sym_list[ap_sym_name] = {'mac': ap['mac'], 'model': ap['model'], 'status': ap['status']}

        return ap_sym_list


    def sort_ap_by_model(self, ap_info_list):
        apd = {}
        for ap in ap_info_list:
            if apd.has_key(ap['model']):
                apd[ap['model']].append(ap)

            else:
                apd[ap['model']] = [ap]

        ap_info_list = []
        for key in sorted(apd.keys()):
            for val in apd[key]:
                ap_info_list.append(val)

        return ap_info_list


    def clear_all_alarms(self):
        """
        Remove all alarms information out of the Alarms table
        """
        self.navigate_to(self.MONITOR, self.MONITOR_ALL_ALARMS)

        #JLIN@20081112 add delay time for ZD implement alarms clear
        self.s.click_and_wait(self.info['loc_mon_alarms_clearall_button'], 5)
#        delete by west:maybe new alarm appear,after clear all alarm
#        total_alarms = self._get_total_number(self.info['loc_mon_total_alarms_span'], "Alarms")
#        if total_alarms != u'0':
#            #JLIN@20081112 print out the alarms number when clear alarms fail
#            raise Exception("Can not clear all the Alarms table, table still has %s alarms" % total_alarms)


    def get_alarms(self,msg=''):
        """
        This function gets all alarms from the Alarms table.
        Output: return a list of lists, in there each list contains all information of one alarm
        """
        self.navigate_to(self.MONITOR, self.MONITOR_ALL_ALARMS, 3)
        if msg:
            search_box=self.info['loc_mon_alarms_search_box']
            t0=time.time()
            while not self.s.is_element_present(search_box):
                if time.time()-t0>600:
                    raise 'search box can not be found after 10 minutes'
                time.sleep(30)
                self.refresh()
            
            self.s.type_text(search_box, '')
            self.s.type_text(search_box,msg)
            self.s.type_keys(search_box,"\013")
            
        time.sleep(3)

        total_alarms = self._get_total_number(self.info['loc_mon_total_alarms_span'], "Alarms")
        logging.info('there are totally %d messages'%int(total_alarms))
        alarms = []
        for i in range(int(total_alarms)):
            one_alarm = []
            time_alarm = self.info['loc_mon_alarms_datetime_cell']
            time_alarm = time_alarm.replace("$_$", str(i))
            time_alarm = self.s.get_text(time_alarm)
            one_alarm.append(time_alarm)

            name = self.info['loc_mon_alarms_name_cell']
            name = name.replace("$_$", str(i))
            name = self.s.get_text(name)
            one_alarm.append(name)

            severity = self.info['loc_mon_alarms_severity_cell']
            severity = severity.replace("$_$", str(i))
            severity = self.s.get_text(severity)
            one_alarm.append(severity)

            activities = self.info['loc_mon_alarms_activities_cell']
            activities = activities.replace("$_$", str(i))
            activities = self.s.get_text(activities)
            one_alarm.append(activities)

            action = self.info['loc_mon_alarms_action_cell']
            action = action.replace("$_$", str(i))
            action = self.s.get_text(action)
            one_alarm.append(action)
            alarms.append(one_alarm)

            if i == 10:
                break

        return alarms


    def clear_all_events(self):
        """
        Remove all events out of the Events/Activites table
        """
        self.navigate_to(self.MONITOR, self.MONITOR_ALL_EVENTS_ACTIVITIES)
        s_time = time.time()
        while time.time() - s_time < 60:
            #Chico, 2014-11-19, the echo speed could be slow in some testbed, so adding it to tolerant
            while True:
                try:           
                    total_events = self._get_total_number(self.info['loc_mon_allevents_total_number_span'], "Events/Activities")
                    break
                except:
                    time.sleep(3)
            #Chico, 2014-11-19, the echo speed could be slow in some testbed, so adding it to tolerant
            if total_events == "0":
                break
            
            self.s.choose_ok_on_next_confirmation()
            self.s.click_and_wait(self.info['loc_mon_allevents_clear_all_button'])
            time.sleep(1)
            if self.s.is_confirmation_present(5):
                logging.info(self.s.get_confirmation())            
                        
            time.sleep(3)
            self.refresh()
        
        from RuckusAutoTest.components.lib.zd import redundancy_zd as sr
        if 'standby' not in sr.get_local_device_state(self):
            self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)
            self.s.click_if_not_checked("//input[@id='high']")
            self.s.click("//input[@id='apply-log']")


    def cfg_syslog_server(self, checked = False, ip_addr = "", log_level = ""):
        """
        Config the Syslog server information to the Zone Director
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)

        if checked:
            if log_level == self.LOG_CRITICAL_WARNING:
                self.s.click_and_wait(self.info['loc_cfg_system_syslog_medium_radio'])

            elif log_level == self.LOG_CRITICAL_ONLY:
                self.s.click_and_wait(self.info['loc_cfg_system_syslog_low_radio'])

            else:
                self.s.click_and_wait(self.info['loc_cfg_system_syslog_high_radio'])

            if not self.s.is_checked(self.info['loc_cfg_system_syslog_enable_checkbox']):
                self.s.click_and_wait(self.info['loc_cfg_system_syslog_enable_checkbox'])

            self.s.type_text(self.info['loc_cfg_system_syslog_server_textbox'], ip_addr)

        else:
            if self.s.is_checked(self.info['loc_cfg_system_syslog_enable_checkbox']):
                self.s.click_and_wait(self.info['loc_cfg_system_syslog_enable_checkbox'])

            if not self.s.is_checked(self.info['loc_cfg_system_syslog_high_radio']):
                self.s.click_and_wait(self.info['loc_cfg_system_syslog_high_radio'])

        self.s.click_and_wait(self.info['loc_cfg_system_syslog_apply_button'], 3)
        if self.s.is_alert_present(5):
            msg = self.s.get_alert()
            raise Exception(msg)

#@author: chen.tao@odc-ruckuswireless.com since 2014-09-04
#To set event log level to high,medium and low.
#It is medium by default
    def set_event_log_level(self,log_level = "high"):
        """
        Config the event log level to the Zone Director
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)

        if log_level == self.LOG_CRITICAL_WARNING:
            self.s.click_and_wait(self.info['loc_cfg_system_syslog_medium_radio'])

        elif log_level == self.LOG_CRITICAL_ONLY:
            self.s.click_and_wait(self.info['loc_cfg_system_syslog_low_radio'])

        else:
            self.s.click_and_wait(self.info['loc_cfg_system_syslog_high_radio'])

        self.s.click_and_wait(self.info['loc_cfg_system_syslog_apply_button'], 3)
        if self.s.is_alert_present(5):
            msg = self.s.get_alert()
            raise Exception(msg)


    def get_system_name(self):
        return self._get_system_name()


    def set_system_name(self, system_name):
        """
        This method is used for setting the System Name with the value given by system_name. It will raise an Exception if an alert
        appears or the name is not set to the system.
        - Input:
            + system_name: a name to apply to the System Name
        - Output: none

        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)

        logging.info("Set the system name to '%s'" % system_name)
        self.s.type(self.info['loc_cfg_system_name_textbox'], system_name)
        self.s.choose_ok_on_next_confirmation()
        self.s.click_and_wait(self.info['loc_cfg_system_name_apply_button'])
        if self.s.is_alert_present(5):
            raise Exception(self.s.get_alert())

        else:
            if self._get_system_name() != system_name:
                if self._get_system_name() != system_name:
                    if self._get_system_name() != system_name:
                        raise Exception("The System Name has not been set on the Dashboard page")

        logging.info("The name '%s' has been set successfully" % system_name)


    def get_ip_cfg(self):
        """
        This method is used for getting the ip configuration of the system.

        - Input:
             + None:
        - Output: a dictionary of IP configuration.
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)
        self.s.click_and_wait(self.info['loc_cfg_system_ip_manual_radio'], 2)

        ip_addr = self.s.get_value(self.info['loc_cfg_system_ip_addr_textbox'])
        net_mask = self.s.get_value(self.info['loc_cfg_system_net_mask_textbox'])
        gateway = self.s.get_value(self.info['loc_cfg_system_gateway_textbox'])
        primary_dns = self.s.get_value(self.info['loc_cfg_system_pri_dns_textbox'])
        secondary_dns = self.s.get_value(self.info['loc_cfg_system_sec_dns_textbox'])
        ip_cfg_dict = {'ip_addr': ip_addr, 'net_mask': net_mask, 'gateway': gateway,
                       'pri_dns': primary_dns, 'sec_dns': secondary_dns}

        return ip_cfg_dict


    def set_ip_cfg(self, ip_cfg_dict, is_cleanup = False):
        """
        This method is used for setting the ip address of the system.

        - Input:
            + ip_cfg_dict: a dictionary of system ip configuration.
        - Output:

        """

        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)
        if self._get_ip_cfg_status() != "static":
            self._set_ip_cfg_status("static")
            time.sleep(2)

        if is_cleanup:
            logging.info("Set the system ip address to '%s'" % ip_cfg_dict['ip_addr'])
            if self.s.is_element_present(self.info['loc_cfg_system_ip_addr_textbox']):
                self.s.type(self.info['loc_cfg_system_ip_addr_textbox'], ip_cfg_dict['ip_addr'])

            logging.info("Set the system net_mask to '%s'" % ip_cfg_dict['net_mask'])
            if self.s.is_element_present(self.info['loc_cfg_system_net_mask_textbox']):
                self.s.type(self.info['loc_cfg_system_net_mask_textbox'], ip_cfg_dict['net_mask'])

            logging.info("Set the system default gateway to '%s'" % ip_cfg_dict['gateway'])
            if self.s.is_element_present(self.info['loc_cfg_system_gateway_textbox']):
                self.s.type(self.info['loc_cfg_system_gateway_textbox'], ip_cfg_dict['gateway'])

            logging.info("Set the system primary dns to '%s'" % ip_cfg_dict['pri_dns'])
            if self.s.is_element_present(self.info['loc_cfg_system_pri_dns_textbox']):
                self.s.type(self.info['loc_cfg_system_pri_dns_textbox'], ip_cfg_dict['pri_dns'])

            logging.info("Set the system secondary dns to '%s'" % ip_cfg_dict['sec_dns'])
            if self.s.is_element_present(self.info['loc_cfg_system_sec_dns_textbox']):
                self.s.type(self.info['loc_cfg_system_sec_dns_textbox'], ip_cfg_dict['sec_dns'])


            self.s.choose_ok_on_next_confirmation()
            self.s.click_and_wait(self.info['loc_cfg_system_mgt_ip_apply_button'], 5)
            if self.s.is_alert_present(5):
                raise Exception (self.s.get_alert())

            self.destroy()
            self.selenium = self.selenium_mgr.create_client(self.browser_type, self.selenium_mgr.to_url(ip_cfg_dict['ip_addr'], True))
            self.started = False # is this WebUI Selenium Client started yet?
            self.s = self.selenium
            self.start()

            if not self.s.is_element_present(self.info['loc_login_username_textbox']):
                self.navigate_to(self.DASHBOARD, self.NOMENU)
                time.sleep(5)
                msg = ''
                if self.s.get_text(self.info['loc_dashboard_sysinfo_ip_cell']) != ip_cfg_dict['ip_addr']:
                    msg = "System IP has not been set on the Dashboard page"

                self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)

                if msg:
                    raise Exception(msg)

            else:
                # Try to re-navigate to the original URL, in case the new IP address can not be set.
                self.destroy()
                self.selenium = self.selenium_mgr.create_client(self.browser_type, self.selenium_mgr.to_url(self.ip_addr, True))
                self.started = False # is this WebUI Selenium Client started yet?
                self.s = self.selenium
                self.start()
                if self.s.is_element_present(self.info['loc_login_username_textbox']):
                    self.current_tab = self.LOGIN_PAGE
                    self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)

            return

        else:

            if ip_cfg_dict['ip_addr']:
                logging.info("Set the system ip address to '%s'" % ip_cfg_dict['ip_addr'])
                if self.s.is_element_present(self.info['loc_cfg_system_ip_addr_textbox']):
                    self.s.type(self.info['loc_cfg_system_ip_addr_textbox'], ip_cfg_dict['ip_addr'])
                    self.s.choose_ok_on_next_confirmation()
                    self.s.click_and_wait(self.info['loc_cfg_system_mgt_ip_apply_button'], 5)
                    if self.s.is_alert_present(5):
                        raise Exception (self.s.get_alert())

                    self.destroy()

                    self.selenium = self.selenium_mgr.create_client(self.browser_type, self.selenium_mgr.to_url(ip_cfg_dict['ip_addr'], True))

                    self.started = False # is this WebUI Selenium Client started yet?
                    self.s = self.selenium
                    
                    self.ip_addr = ip_cfg_dict['ip_addr']
                    self.conf['url.login'] = "https://" + ip_cfg_dict['ip_addr'] + "/admin/login.jsp"
       
                    self.start()
                    time.sleep(10)

                    if not self.s.is_element_present(self.info['loc_login_username_textbox']):
                        self.navigate_to(self.DASHBOARD, self.NOMENU)
                        time.sleep(5)
                        msg = ''
                        if self.s.get_text(self.info['loc_dashboard_sysinfo_ip_cell']) != ip_cfg_dict['ip_addr']:
                            msg = "System IP has not been set on the Dashboard page"

                        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)
                        if msg:
                            raise Exception(msg)

                    else:
                        # Try to re-navigate to the original URL, in case the new IP address can not be set.
                        self.destroy()

                        self.selenium = self.selenium_mgr.create_client(self.browser_type, self.selenium_mgr.to_url(self.ip_addr, True))

                        self.started = False # is this WebUI Selenium Client started yet?
                        self.s = self.selenium

                        self.start()

                        if self.s.is_element_present(self.info['loc_login_username_textbox']):
                            self.current_tab = self.LOGIN_PAGE
                            self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)


            if ip_cfg_dict['net_mask']:
                logging.info("Set the system net_mask to '%s'" % ip_cfg_dict['net_mask'])
                if self.s.is_element_present(self.info['loc_cfg_system_net_mask_textbox']):
                    self.s.type(self.info['loc_cfg_system_net_mask_textbox'], ip_cfg_dict['net_mask'])
                    self.s.choose_ok_on_next_confirmation()
                    self.s.click_and_wait(self.info['loc_cfg_system_mgt_ip_apply_button'], 5)
                    if self.s.is_alert_present(5):
                        raise Exception (self.s.get_alert())

            if ip_cfg_dict['gateway']:
                logging.info("Set the system default gateway to '%s'" % ip_cfg_dict['gateway'])
                if self.s.is_element_present(self.info['loc_cfg_system_gateway_textbox']):
                    self.s.type(self.info['loc_cfg_system_gateway_textbox'], ip_cfg_dict['gateway'])
                    self.s.choose_ok_on_next_confirmation()
                    self.s.click_and_wait(self.info['loc_cfg_system_mgt_ip_apply_button'], 5)
                    if self.s.is_alert_present(5):
                        raise Exception (self.s.get_alert())

            if ip_cfg_dict['pri_dns']:
                logging.info("Set the system primary dns to '%s'" % ip_cfg_dict['pri_dns'])
                if self.s.is_element_present(self.info['loc_cfg_system_pri_dns_textbox']):
                    self.s.type(self.info['loc_cfg_system_pri_dns_textbox'], ip_cfg_dict['pri_dns'])
                    self.s.choose_ok_on_next_confirmation()
                    self.s.click_and_wait(self.info['loc_cfg_system_mgt_ip_apply_button'], 5)
                    if self.s.is_alert_present(5):
                        raise Exception (self.s.get_alert())

            if ip_cfg_dict['sec_dns']:
                logging.info("Set the system secondary dns to '%s'" % ip_cfg_dict['sec_dns'])
                if self.s.is_element_present(self.info['loc_cfg_system_sec_dns_textbox']):
                    self.s.type(self.info['loc_cfg_system_sec_dns_textbox'], ip_cfg_dict['sec_dns'])
                    self.s.choose_ok_on_next_confirmation()
                    self.s.click_and_wait(self.info['loc_cfg_system_mgt_ip_apply_button'], 5)
                    if self.s.is_alert_present(5):
                        raise Exception (self.s.get_alert())


    def get_ip_cfg_status(self):
        return self._get_ip_cfg_status()


    def set_ip_cfg_status(self, status):
        self._set_ip_cfg_status(status)


    def setup_wizard_cfg(self, default_conf = {}, new_conf = {}):
        self._reset_factory()
        self._setup_wizard_cfg(default_conf, new_conf)


    def get_serial_number(self):
        return self._get_serial_number()


    def create_radius_server(self, ras_addr, ras_port, ras_secret, server_name = "", radius_auth_method = "pap"):
        '''
        WARNING: OBSOLETE, use create_server in lib.zd.aaa instead
        '''
        params = {'server_addr': ras_addr, 'server_port': ras_port,
                  'server_name': server_name,
                  'radius_auth_secret': ras_secret, 
                  'radius_auth_method': radius_auth_method,}
        return AAA.create_server(self, **params)


    def create_ad_server(self, ad_addr, ad_port, ad_domain, server_name = ""):
        '''
        WARNING: OBSOLETE, use create_server in lib.zd.aaa instead
        '''
        params = {'server_addr': ad_addr, 'server_port': ad_port,
                  'server_name': server_name,
                  'win_domain_name': ad_domain}
        return AAA.create_server(self, **params)

        # PHANNT@20100602: never calls the below old method
        # this will be cleaned up at a later time
        self._create_ad_server(ad_addr, ad_port, ad_domain, server_name)


    def remove_all_auth_servers(self):
        '''
        WARNING: OBSOLETE, use remove_all_servers in lib.zd.aaa instead
        '''
        return AAA.remove_all_servers(self)

        # PHANNT@20100602: never calls the below old method
        # this will be cleaned up at a later time
        self._delete_all_auth_server()


    def remove_all_users(self):
        """
        Remove all users out of users table.
        """
        while True:
            if not self._delete_all_user():
                break


    def create_user(self, username, password, fullname = "", role = 'Default', number_of_users = 1):
        """
        Create a number of users. By default just create one user.
        """
        user_role = role
        if number_of_users > 1:
            self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS)
            for i in range(number_of_users):
                self._create_user('%s_%d' % (username, i), password,
                                  role = user_role, is_config_user_page = True)
                time.sleep(3)

        else:
            self._create_user(username, password, fullname, role)


    def get_number_users(self):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS, 2)
        locator = self.info['loc_cfg_user_total_number_span']

        number_users = self.s.get_text(locator)
        if not number_users:
            time.sleep(5)
            number_users = self.s.get_text(locator)

        time.sleep(1)
        pat = ".*\(([0-9]+)\)$"
        match_obj = re.search(pat, number_users)
        if match_obj:
            number_users = match_obj.group(1)

        else:
            raise Exception("Can not get the total number of rows in Users table")

        time.sleep(3)

        return int(number_users)


    def delete_user(self, username):
        self._delete_user(username)


    def remove_all_guestpasses(self):
        self._delete_all_guestpasses()


    def generate_guestpass(self, username, password, guest_fullname, duration, duration_unit, remarks = '',
                           key = '', validate_gprints = False):
        """
        This method is used for getting the guestpass with the given username and password
        (on authentication server or Local Database)
        - Input:
            + username: user for authenticating
            + password: password for authenticating
            + guest_fullname: full name of the guestpass
            + duration: is a number of duration unit
            + duration_unit: is either Days, Hours or Weeks
            + remarks:
        - Output:
            + Guestpass:
            + Expired time:
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS, 2)
        guestpass_url = self.s.get_text(self.info['loc_cfg_guestaccess_guestpass_url_span'])
        logging.info("Navigate to the guestpass url: '%s'" % guestpass_url)
        self.s.open(guestpass_url)

        self.s.wait_for_page_to_load(self.conf['loadtime_open2'])
        logging.info("Fill authentication username '%s' and password '%s'" % (username, password))
        self.s.type_text(self.info['loc_guestpass_username_textbox'], username)
        self.s.type_text(self.info['loc_guestpass_password_textbox'], password)
        self.s.click_and_wait(self.info['loc_guestpass_login_button'])

        if self.s.is_element_present(self.info['loc_guestpass_loginfailed_div']):
            error_msg = self.s.get_text(self.info['loc_guestpass_loginfailed_div'])
            logging.info("Error: %s" % error_msg)
            logging.info("Navigate to the ZoneDirector's url.")
            self.s.open(self.url)
            self.current_tab = self.LOGIN_PAGE
            self.s.wait_for_page_to_load(self.conf['loadtime_login'])
            raise Exception(error_msg)

        # Fill the information of the guest pass
        logging.info("Fill the guest pass information---Fullname: '%s', duration: '%s', duration unit: '%s', remarks:'%s'" % \
                     (guest_fullname, duration, duration_unit, remarks))
        self.s.type_text(self.info['loc_guestinfo_fullname_textbox'], guest_fullname)
        self.s.type_text(self.info['loc_guestinfo_duration_textbox'], duration)
        self.s.select_option(self.info['loc_guestinfo_duration_unit_option'], duration_unit)
        if remarks:
            self.s.type_text(self.info['loc_guestinfo_remarks_textarea'], remarks)

        if key:
            self.s.type_text(self.info['loc_guestinfo_key_textbox'], key)

        self.s.click_and_wait(self.info['loc_guestinfo_next_button'], 2)

        # Get the expired time and the GUEST PASS
        logging.info("Get the guestpass and expired time")
        expired_time = self.s.get_text(self.info['loc_guestpass_dialog_expire_span'])
        logging.info("The expired time is '%s'" % expired_time)
        guest_pass = self.s.get_text(self.info['loc_guestpass_dialog_pass_div'])
        logging.info("The guestpass is '%s'" % guest_pass)

        guest_name_all = self.s.get_text(self.info['loc_guestpass_guest_name_text'])
        #u'Here is the generated guest pass for aa'
        guest_name = re.match('.*the generated guest pass for (.*)',guest_name_all).group(1)
        logging.info("The guest name is '%s'" % guest_name)

        if validate_gprints:
            self.__verify_guestpass_printouts(guest_name, guest_pass, expired_time)

        # Finish generating guest pass
        logging.info("Navigate to the Zone Director's url")
        self.s.open(self.url)
        self.current_tab = self.LOGIN_PAGE
        self.s.wait_for_page_to_load(self.conf['loadtime_login'])

        if not expired_time:
            raise Exception("Can not get the expired time for the user '%s'" % username)

        if not guest_pass:
            raise Exception("Can not get the guest pass for the user '%s'" % username)

        return (guest_pass, expired_time)

    def __verify_guestpass_printouts(self, guest_name, guest_pass, expired_time):
        guest_info = {'guest name': guest_name, 'guest pass': guest_pass, 'expired time': expired_time}

        # This dialog handler closes any Print dialogs launched by the Guest Pass Printout window
        dlg_mgr = DialogManager()
        dlg_mgr.add_dialog(BaseDialog("Print", "", "Cancel"))
        dlg_mgr.start()

        # Obtain list of Guest Pass Printouts
        gprints = self.s.get_select_options(self.info['loc_guestpass_printout_option'])

        # Obtain the current window names
        win_names = self.s.get_all_window_names()

        for gprint in gprints:
            logging.info("Open the Guest Pass Printout [%s] and verify its content" % gprint)
            self.s.select_option(self.info['loc_guestpass_printout_option'], gprint)
            self.s.click_and_wait(self.info['loc_guestpass_print_instruction_anchor'], 3)

            # Find the new window's name
            new_win_name = [name for name in self.s.get_all_window_names() \
                            if name != 'null' and \
                               'selenium_blank' not in name and \
                               name not in win_names][0]

            # Verify its content
            try:
                self.s.select_window(new_win_name)
                gprint_content = self.s.get_body_text()
                for k, v in guest_info.items():
                    if v not in gprint_content:
                        raise Exception("[%s] was not found or it was not [%s] in the Guest Pass Printout [%s]" % (k, v, gprint))

            except:
                # Stop the dialog manager
                dlg_mgr.shutdown()
                dlg_mgr.join(10)

            finally:
                for name in self.s.get_all_window_names():
                    if name != 'null' and name not in win_names:
                        self.s.select_window(name)
                        self.s.close()

                self.s.select_window('')

        # Stop the dialog manager
        dlg_mgr.shutdown()
        dlg_mgr.join(10)


    def get_events(self):
        #cwang@2010-11-1, behavior change, span tag --> select tag
        """
        Get all events from the Events/Activites table
        Output: return a list of lists, in there, each list contains all information of each event
        """
        self.navigate_to(self.MONITOR, self.MONITOR_ALL_EVENTS_ACTIVITIES, 2)
        total_events = self._get_total_number(self.info['loc_mon_allevents_total_number_span'], "Events/Activities")
        if int(total_events) == 0:
            return []

        events = []
        total_number_span = self.info['loc_mon_allevents_total_number_span']
        value_index = 1
        while True:
            event_count_text = self.s.get_text(total_number_span)
            select_tag_loc = self.info['loc_mon_allevents_number_select_option'] % value_index
            start_idx = 0
            end_idx = 0
            if not self.s.is_element_present(select_tag_loc) or not self.s.is_element_visible(select_tag_loc):
                m = re.match("(\d+)-(\d+) \((\d+)\)", event_count_text)
                if not m:
                    raise Exception("Unable to parse the total event number '%s'" % event_count_text)
                start_idx = int(m.group(1))
                end_idx = int(m.group(2))
                total_number = int(m.group(3))
            else:
                m = re.match("\((\d+)\)", event_count_text)
                if not m:
                    raise Exception("Unable to parse the total event number '%s'" % event_count_text)
                total_number = int(m.group(1))

                number_span_text = self.s.get_text(select_tag_loc)
                m = re.match("(\d+)-(\d+)", number_span_text)
                if not m:
                    raise Exception("Unable to parse the total event number '%s'" % number_span_text)

                start_idx = int(m.group(1))
                end_idx = int(m.group(2))

            if total_number == 0: break

            number_of_entries = end_idx - start_idx + 1
            for i in range(number_of_entries):
                row_idx = i + start_idx - 1
                one_event = []
                time_event = self.info['loc_mon_allevents_time_cell']
                time_event = time_event.replace("$_$", str(row_idx))
                time_event = self.s.get_text(time_event)
                one_event.append(time_event)

                severity = self.info['loc_mon_allevents_severity_cell']
                severity = severity.replace("$_$", str(row_idx))
                severity = self.s.get_text(severity)
                one_event.append(severity)

                user = self.info['loc_mon_allevents_user_cell']
                user = user.replace("$_$", str(row_idx))
                user = self.s.get_text(user)
                one_event.append(user)

                activities = self.info['loc_mon_allevents_activities_cell']
                activities = activities.replace("$_$", str(row_idx))
                activities = self.s.get_text(activities)
                one_event.append(activities)

                events.append(one_event)

            if end_idx == total_number:
                break

            self.s.click_and_wait(self.info['loc_mon_allevents_next_img'], 3)
            value_index += 1

        return events



    def set_alarm_email(self, email_addr, mail_server_addr, check = True):
 ############@zhangjie20140523 optimize for email alarm behavior change zf-8437
        alt_get1 = ""
        alt_get2 = ""
        try:
            asz.set_alarm_email_syscfg(self,email_addr)
        except Exception,e:
            alt_get1 = e.message
            
        try:
            asz.set_alarm_email_alarmcfg(self,email_addr)
        except Exception,e:
            alt_get2 = e.message
            
        return alt_get1,alt_get2
############@zhangjie20140523 optimize for email alarm behavior change 

##################################################################################################
#        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ALARM_SETTINGS)
#        #####zj behavior change: ZF-7694
#        xlocs = asz.LOCATORS_CFG_ALARM_SETTINGS
#        from_email_addr = 'lab@example.net'
#        server_name = '192.168.0.252'
#        server_port = '25'
#        username = 'lab'
#        password = 'lab4man1'
#
#        checkbox = self.info['loc_cfg_system_alarm_doemail_checkbox']
##@author: chen.tao since 2013-10-16 to support 9.8 email alarm settings.
#        if (not self.s.is_checked(checkbox)) and check:
#            self.s.click_and_wait(checkbox)
#            self.s.type_text(self.info['loc_cfg_system_alarm_email_textbox'], email_addr)
#            self.s.click_and_wait(self.info['loc_cfg_system_alarm_notify_apply_button'])
#
#            self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)
#            self.s.type_text(self.info['loc_cfg_system_alarm_smtp_ip_textbox'], mail_server_addr)
#        #####zj behavior change  ZF-7694: need configure: "From Email Address" ,  SMTP Server Port,  Username, Password,   Confirm Password
#            self.s.type_text(xlocs['email_from_textbox'], from_email_addr)
#            self.s.type_text(xlocs['smtp_port_textbox'], server_port)
#            self.s.type_text(xlocs['username_textbox'], username)
#            self.s.type_text(xlocs['password_textbox'], password)
#            self.s.type_text(xlocs['confirm_password_textbox'], password)
#        #####zj behavior change ZF-7694: need configure: "From Email Address" ,  SMTP Server Port,  Username, Password,   Confirm Password
#            self.s.click_and_wait(self.info['loc_cfg_system_alarm_apply_button'])
# 
#        if (not check) and self.s.is_checked(checkbox):
#            self.s.type(self.info['loc_cfg_system_alarm_email_textbox'], email_addr)
#            self.s.click_and_wait(checkbox)
#            self.s.click_and_wait(self.info['loc_cfg_system_alarm_notify_apply_button'])
#            
#            self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)
#            self.s.type(self.info['loc_cfg_system_alarm_smtp_ip_textbox'], mail_server_addr)
#        #####zj behavior change  ZF-7694: need configure: "From Email Address" ,  SMTP Server Port,  Username, Password,   Confirm Password
#            self.s.type_text(xlocs['email_from_textbox'], from_email_addr)
#            self.s.type_text(xlocs['smtp_port_textbox'], server_port)
#            self.s.type_text(xlocs['username_textbox'], username)
#            self.s.type_text(xlocs['password_textbox'], password)
#            self.s.type_text(xlocs['confirm_password_textbox'], password)
#        #####zj behavior change ZF-7694: need configure: "From Email Address" ,  SMTP Server Port,  Username, Password,   Confirm Password
#            self.s.click_and_wait(self.info['loc_cfg_system_alarm_apply_button'])
##@author: chen.tao since 2013-10-16 to support 9.8 email alarm settings.
#
#        if self.s.is_alert_present(5):
#            raise Exception(self.s.get_alert())


    def get_alarm_email(self):
        '''
        return dict:
        {'email_addr':'',
         'mail_server_addr':'',
        }
        '''
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ALARM_SETTINGS)
        #@zhangjie20140523 optimize for email alarm behavior change 
        checkbox = self.info['loc_cfg_alarm_settings_doemail_checkbox']
        if not self.s.is_checked(checkbox):
            return None
        cfg = {'email_addr':'',
               'mail_server_addr':''
              }
        #@zhangjie20140523 optimize for email alarm behavior change 
        cfg['email_addr'] = self.s.get_value(self.info['loc_cfg_alarm_settings_email_textbox'])
        #@author: chen.tao since 2013-10-16 to support 9.8 email alarm settings.
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM)
        #@author: chen.tao since 2013-10-16 to support 9.8 email alarm settings.
        cfg['mail_server_addr'] = self.s.get_value(self.info['loc_cfg_system_alarm_smtp_ip_textbox'])
        return cfg
    
    def alarm_email_enabled_check(self):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ALARM_SETTINGS)
        #@zhangjie20140523 optimize for email alarm behavior change 
        checkbox = self.info['loc_cfg_alarm_settings_doemail_checkbox']
        if not self.s.is_checked(checkbox):
            return False
        else:
            return True
        
    def disable_alarm_email(self):
#        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ALARM_SETTINGS)
#        checkbox = self.info['loc_cfg_alarm_settings_doemail_checkbox']
#        self.s.click_if_checked(checkbox)
#        time.sleep(0.5)
#        #@author: chen.tao since 2013-10-16 to support 9.8 email alarm settings.
#        self.s.click_and_wait(self.info['loc_cfg_alarm_settings_notify_apply_button'])
#        #@author: chen.tao since 2013-10-16 to support 9.8 email alarm settings.
#        if self.s.is_alert_present(5):
#            raise Exception(self.s.get_alert())
#
############@zhangjie20140523 optimize for email alarm behavior change 
        alt_get1 = ""
        alt_get2 = ""
        try:
            asz.clear_syscfg_alarm_settings(self)
        except Exception,e:
            alt_get1 = e.message
                
        try:
            asz.clear_alarm_settings(self)
        except Exception,e:
            alt_get2 = e.message
                
        return alt_get1,alt_get2 
############@zhangjie20140523 optimize for email alarm behavior change     
   
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
    def create_guestaccess_policy(self, use_guestpass_auth = True, use_tou = False,
                               redirect_url = "", enable_share_guestpass = False,
                               onboarding_portal = False, selfservice=False
                               ):
        """
        This function configures the Guest Access Policy to specified info
        @param use_guest_auth: A boolean value indicates that Guest Pass authen is used or not
        @param use_tou: A boolean value indicates that TOU is used or not
        @param redirect_url: A string holds the URL that is redirected to; use NULL to disable this feature
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS)

        #shared = self.info['loc_cfg_guestaccess_shared_guestpass_checkbox']
        boarding = self.info['loc_cfg_guestaccess_boarding_portal_checkbox']
        auth = self.info['loc_cfg_guestaccess_guestauth_radio']
        no_auth = self.info['loc_cfg_guestaccess_no_guestauth_radio']
        tou = self.info['loc_cfg_guestaccess_show_tou_checkbox']
        selfser = self.info['loc_cfg_guestpass_selfservice_check_box']
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        create_new_span = self.info['loc_cfg_guest_access_new_span']
        gc_name = self.info['loc_cfg_guest_access_name']
        if self.s.is_element_disabled(create_new_span, timeout = 1):
            raise Exception("Unable to create more when the 'Create New' button is disabled.") 
        self.s.click_and_wait(create_new_span)
        self.s.type_text(gc_name, DEFAULT_GUEST_ACCESS_NAME)
        
        if self.s.is_element_present(selfser, 2):
            if not selfservice:
                self.s.uncheck(selfser)
            else:
                self.s.check(selfser)
        else:
            if older_than_release(self.version['version'],'9.9.1.0'):#Chico, 2015-6-29, optimize to cover future releases
                pass
            else:
                raise Exception("Element '%s' doesn't exist." % selfser)
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226

        #@author: Jane.Guo @since: 20130608pm to adapt to 9.7 build, don't include boarding
        if self.s.is_element_present(boarding):
            if onboarding_portal:
                if not self.s.is_checked(boarding):
                    self.s.click_and_wait(boarding)
            else:
                if self.s.is_checked(boarding):
                    self.s.click_and_wait(boarding)

        if use_guestpass_auth:
            self.s.click_and_wait(auth)
#            if enable_share_guestpass:
#                if not self.s.is_checked(shared):
#                    self.s.click_and_wait(shared)
#
#            else:
#                if self.s.is_checked(shared):
#                    self.s.click_and_wait(shared)

        else:
            self.s.click_and_wait(no_auth)

        if use_tou:
            if not self.s.is_checked(tou):
                self.s.click_and_wait(tou)

        else:
            if self.s.is_checked(tou):
                self.s.click_and_wait(tou)

        if redirect_url:
            self.s.click_and_wait(self.info['loc_cfg_guestaccess_redirect_url_radio'])
            self.s.type_text(self.info['loc_cfg_guestaccess_redirect_url_textbox'], redirect_url)

        else:
            self.s.click_and_wait(self.info['loc_cfg_guestaccess_redirect_orig_radio'])

        self.s.click_and_wait(self.info['loc_cfg_guest_access_ok'])
        time.sleep(5)

        if self.s.is_alert_present(5):
            raise Exception(self.s.get_alert())

    def delete_guestaccess_policy(self, name=''):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        check_before = self.info['loc_cfg_guest_access_check_box_before_profile'] % str(0)
        delete_span = self.info['loc_cfg_guest_access_delete_span']
        time.sleep(2)
        self.s.click_and_wait(check_before)
        self.s.click_and_wait(delete_span)
        return

    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
    def set_guestaccess_policy(self, use_guestpass_auth = True, use_tou = False,
                               redirect_url = "", enable_share_guestpass = False,
                               onboarding_portal = False, selfservice=False
                               ):
        """
        This function configures the Guest Access Policy to specified info
        @param use_guest_auth: A boolean value indicates that Guest Pass authen is used or not
        @param use_tou: A boolean value indicates that TOU is used or not
        @param redirect_url: A string holds the URL that is redirected to; use NULL to disable this feature
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS)

        #shared = self.info['loc_cfg_guestaccess_shared_guestpass_checkbox']
        boarding = self.info['loc_cfg_guestaccess_boarding_portal_checkbox']
        auth = self.info['loc_cfg_guestaccess_guestauth_radio']
        no_auth = self.info['loc_cfg_guestaccess_no_guestauth_radio']
        tou = self.info['loc_cfg_guestaccess_show_tou_checkbox']
        selfser = self.info['loc_cfg_guestpass_selfservice_check_box']

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = self.info['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        if not self.s.is_element_present(edit_span):
            self.create_guestaccess_policy()
        time.sleep(2)
        self.s.click_and_wait(edit_span)
        
        if self.s.is_element_present(selfser, 2):
            if not selfservice:
                self.s.uncheck(selfser)
            else:
                self.s.check(selfser)
        else:
            if older_than_release(self.version['version'], '9.9.1.0'):#Chico, 2015-6-29, optimize to cover future releases
                pass
            else:
                raise Exception("Element '%s' doesn't exist." % selfser)
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
        
        #@author: Jane.Guo @since: 20130608pm to adapt to 9.7 build, don't include boarding
        if self.s.is_element_present(boarding):
            if onboarding_portal:
                if not self.s.is_checked(boarding):
                    self.s.click_and_wait(boarding)
            else:
                if self.s.is_checked(boarding):
                    self.s.click_and_wait(boarding)

        if use_guestpass_auth:
            self.s.click_and_wait(auth)
#            if enable_share_guestpass:
#                if not self.s.is_checked(shared):
#                    self.s.click_and_wait(shared)
#
#            else:
#                if self.s.is_checked(shared):
#                    self.s.click_and_wait(shared)

        else:
            self.s.click_and_wait(no_auth)

        if use_tou:
            if not self.s.is_checked(tou):
                self.s.click_and_wait(tou)

        else:
            if self.s.is_checked(tou):
                self.s.click_and_wait(tou)

        if redirect_url:
            self.s.click_and_wait(self.info['loc_cfg_guestaccess_redirect_url_radio'])
            self.s.type_text(self.info['loc_cfg_guestaccess_redirect_url_textbox'], redirect_url)

        else:
            self.s.click_and_wait(self.info['loc_cfg_guestaccess_redirect_orig_radio'])

        self.s.click_and_wait(self.info['loc_cfg_guest_access_ok'])
        time.sleep(2)

        if self.s.is_alert_present(5):
            raise Exception(self.s.get_alert())


    def get_guestaccess_policy(self):
        """
        This function returns a dictionary contains information about current
        Guest Access Policy configured on the ZD
        @return: a dictionary with following keys:
            - use_guestpass_auth: True/False
            - enable_share_guestpass: True/False
            - use_tou: True/False
            - redirect_url: a string represent the redirected URL
                            the string is NULL when this feature is not used
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = self.info['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        #chen.tao 2014-03-17, to fix ZF-7418
        if not self.s.is_element_present(edit_span):
            return
        time.sleep(2)
        self.s.click_and_wait(edit_span)
        
        guest_access_policy = {}

        boarding = self.info['loc_cfg_guestaccess_boarding_portal_checkbox']
        #@author: Jane.Guo @since: 20130608pm to adapt to 9.7 build, don't include boarding
        if self.s.is_element_present(boarding):
            if self.s.is_checked(boarding):
                guest_access_policy['onboarding_portal'] = True
            else:
                guest_access_policy['onboarding_portal'] = False
        
        if self.s.is_checked(self.info['loc_cfg_guestaccess_guestauth_radio']):
            guest_access_policy['use_guestpass_auth'] = True
            
            #@author: Anzuo, this xpath has been deleted
#            if self.s.is_checked(self.info['loc_cfg_guestaccess_shared_guestpass_checkbox']):
#                guest_access_policy['enable_share_guestpass'] = True
#
#            else:
#                guest_access_policy['enable_share_guestpass'] = False

        else:
            guest_access_policy['use_guestpass_auth'] = False
            guest_access_policy['enable_share_guestpass'] = False

        if self.s.is_checked(self.info['loc_cfg_guestaccess_show_tou_checkbox']):
            guest_access_policy['use_tou'] = True
        else:
            guest_access_policy['use_tou'] = False

        if self.s.is_checked(self.info['loc_cfg_guestaccess_redirect_url_radio']):
            guest_access_policy['redirect_url'] = self.s.get_value(self.info['loc_cfg_guestaccess_redirect_url_textbox'])
        else:
            guest_access_policy['redirect_url'] = ""

        return guest_access_policy


    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226
    def set_guestpass_policy(self, auth_serv = "", is_first_use_expired = False, valid_day = '5', expired_set = False, service_name=DEFAULT_GUEST_ACCESS_NAME):
        """
        Refer to the function _set_guestpass_policy to see the docstring
        """
        self._set_guestpass_policy(auth_serv, is_first_use_expired, valid_day, expired_set, service_name)

    def _set_guestpass_policy(self, auth_serv, is_first_use_expired, valid_day, expired_set, service_name):
        """
        This function is used to set policy for a guest pass. It will choose database for guestpass authentication,
        set guestpass expiration policy
        Input:
        - auth_serv: name of database used for guestpass authentication, ex: Local Database
        - is_first_use_expired: If it's True, the guestpass will expire in the amount of specified time after it's first used.
        If it's False, the guestpass will expired in the amount of time after it's issued.
        - valid_day: the maximum valid time of a guest pass (using when is_first_use_expired is True)
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS)

        logging.info("Choose the database '%s' for guestpass authentication" % auth_serv)
        self.s.select_option(self.info['loc_cfg_guestaccess_auth_server_option'], auth_serv)
        time.sleep(1)
        self.s.click_and_wait(self.info['loc_cfg_guestaccess_guestpass_apply_button'])

        if expired_set:
            edit_span = self.info['loc_cfg_guest_access_edit_span'] % service_name
            self.s.click_and_wait(edit_span)
            if is_first_use_expired:
                self.s.click_and_wait(self.info['loc_cfg_guestpass_countdown_by_used_radio'])
                self.s.type(self.info['loc_cfg_guestpass_guestvalid_textbox'], valid_day)
            else:
                self.s.click_and_wait(self.info['loc_cfg_guestpass_countdown_by_issued_radio'])
            time.sleep(2)
            self.s.click_and_wait(self.info['loc_cfg_guest_access_ok'])

        if self.s.is_alert_present(5):
            msg_alert = self.s.get_alert()
            raise Exception(msg_alert)
    #@author: Chico, @since:2014-12-17, ZD 9.10 adds guest access self service, bug ZF-11226

    def get_guestpass_policy(self):
        """
        This function is used to get information of guest pass policy, including the guestpass expiration policy,
        and name of authentication server that used to generate a guestpass.
        Input: none
        Output: return a dictionary of information about guest pass policy
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS, 2)

        guest_pass_policy = {}
        if not self.s.is_element_present(self.info['loc_cfg_guestaccess_auth_server_option']):
            raise Exception("Element %s not found" % self.info['loc_cfg_guestaccess_auth_server_option'])

        guest_pass_policy['auth_serv'] = self.s.get_selected_label(self.info['loc_cfg_guestaccess_auth_server_option'])
        if self.s.is_checked(self.info['loc_cfg_guestpass_countdown_by_issued_radio']):
            guest_pass_policy['is_first_use_expired'] = False
            guest_pass_policy['valid_day'] = ''

        else:
            guest_pass_policy['is_first_use_expired'] = True
            guest_pass_policy['valid_day'] = self.s.get_value(self.info['loc_cfg_guestpass_guestvalid_textbox'])

        return guest_pass_policy


    #JLIN@20081210 modified it for ZD8.0
    def set_restricted_subnets(self, restricted_subnet_list):
        """
        This function configures the restricted subnet access with given subnet addresses in
        format 192.168.1.0/24
        @param restricted_subnet_list: list of addresses in the format mentioned above
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS, 3)
        max_rule = 32
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = self.info['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        self.s.click_and_wait(edit_span)
        self.s.click_and_wait(self.info['loc_cfg_guest_access_restrict_list'])

        for i in range(len(restricted_subnet_list)):
            rule_num = i + 2
            locator = self.info['loc_cfg_restricted_rule_edit_span']
            locator = locator.replace("$_$", str(i + 1))
            if self.s.is_element_present(locator):
                self.s.click_and_wait(locator)

            else:
                self.s.click_and_wait(self.info['loc_cfg_restricted_rule_create_span'])
                self.s.select_option(self.info['loc_cfg_restricted_rule_order_select'], str(rule_num))

            self.s.type_text(self.info['loc_cfg_restricted_rule_dst_addr'], restricted_subnet_list[i])
            self.s.click_and_wait(self.info['loc_cfg_restricted_rule_ok_button'])
            if (self.s.is_alert_present(5)):
                msg_alert = self.s.get_alert()
                raise Exception(msg_alert)

        #delete rules beside restricted_subnet_list
        bugme.do_trace("TRACE_RAT_RES")
        while True:
            locator = self.info['loc_cfg_restricted_rule_checkbox']
            locator = locator.replace("$_$", str(len(restricted_subnet_list) + 2))
            if self.s.is_element_present(locator):
                self.s.click_and_wait(locator)
                self.s.click_and_wait(self.info['loc_cfg_restricted_rule_del_button'])
                if (self.s.is_alert_present(5)):
                    msg_alert = self.s.get_alert()
                    raise Exception(msg_alert)

            else:
                break

        self.s.click_and_wait(self.info['loc_cfg_guest_access_ok'])
        time.sleep(5)

    #JLIN@20081209 modified it for ZD8.0
    def get_restricted_subnets(self):
        """
        This function returns a list of subnets that are restricted to access to wireless
        guest users
        @return: a list of addresses in format 192.168.1.0/24
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
        edit_span = self.info['loc_cfg_guest_access_edit_span'] % DEFAULT_GUEST_ACCESS_NAME
        time.sleep(2)
        self.s.click_and_wait(edit_span)
        self.s.click_and_wait(self.info['loc_cfg_guest_access_restrict_list'])
        
        subnet_list = []
        i = 1
        while True:
            i = i + 1
            locator = self.info['loc_cfg_restricted_rule_row']
            locator = locator.replace("$_$", str(i))
            time.sleep(3)
            if self.s.is_element_present(locator):
                locator = self.info['loc_cfg_restricted_subnets_textbox']
                locator = locator.replace("$_$", str(i))
                subnet = self.s.get_text(locator)
                subnet_list.append(subnet)

            else:
                break
        self.s.click_and_wait(self.info['loc_cfg_guest_access_cancel'])
        time.sleep(1)

        return subnet_list


    def remove_rogue_aps(self, is_marked = True):
        self.navigate_to(self.MONITOR, self.MONITOR_ROGUE_DEVICES)
        if is_marked:
            self._mark_rogue_ap()

        else:
            self._remove_known_rogue_ap()


    def get_all_acl_names(self):
        """
        This function returns a list of names of ACL on the ZoneDirector
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_CONTROLS, 3)

        total_acls = self._get_total_number(self.info['loc_cfg_total_acls_span'], "Access Controls")
        max_acls_row = int(self.info['const_cfg_max_acl_rows'])
        traverse_row = 1
        i = 0
        total_entries = []

        if total_acls == u'0':
            logging.info("There's no ACL rules in the Access Controls table")
            return []

        while i < int(total_acls):
            find_acl_name = self.info['loc_cfg_acl_name_cell']
            find_acl_name = find_acl_name.replace('$_$', str(traverse_row))
            get_acl_name = self.s.get_text(find_acl_name)
            total_entries.append(get_acl_name)

            if traverse_row == max_acls_row:
                traverse_row = 0
                self.s.click_and_wait(self.info['loc_cfg_acl_next_image'])
            traverse_row += 1
            i += 1
            time.sleep(1)

        return total_entries


    def get_acl_info(self, acl_name):
        """
        Get all information of particular ACL shown by acl_name.
        Input:
        - acl_name: name of an AP.
        Output: return a dictionary of information of ACL (policy, mac address, name)
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_CONTROLS, 3)

        total_acls = self._get_total_number(self.info['loc_cfg_total_acls_span'], "Access Controls")
        max_acls_row = int(self.info['const_cfg_max_acl_rows'])
        traverse_row = 1
        i = 0
        acl_info = {}

        if total_acls == u'0':
            logging.info("There's no acl rules in the Access Controls table")
            return {}

        while i < int(total_acls):
            find_acl_name = self.info['loc_cfg_acl_name_cell']
            find_acl_name = find_acl_name.replace('$_$', str(traverse_row))
            get_acl_name = self.s.get_text(find_acl_name)

            if get_acl_name == acl_name:
                acl_edit = self.info['loc_cfg_acl_edit_span']
                acl_edit = acl_edit.replace('$_$', str(i))
                self.s.click_and_wait(acl_edit)

                acl_info['acl_name'] = acl_name
                if self.s.is_checked(self.info['loc_cfg_acl_allowall_radio']):
                    acl_info['policy'] = 'allow-all'

                else:
                    acl_info['policy'] = 'deny-all'

                acl_info['mac_entries'] = self.s.get_text(self.info['loc_cfg_acl_mac_table']).split('delete')[:-1]
                break

            if traverse_row == max_acls_row:
                traverse_row = 0
                self.s.click_and_wait(self.info['loc_cfg_acl_next_image'])

            traverse_row += 1
            i += 1
            time.sleep(1)

        return acl_info


    def create_acl_rule(self, acl_name_list, mac_list, acl_policy):
        """
        This function creates one or many acl rules based on the list of ACL names.
        Input: refer to the function _create_acl_rule to see the definition of input parameters
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_CONTROLS)

        for acl_name in acl_name_list:
            self._create_acl_rule(acl_name, acl_policy, mac_list)
            time.sleep(4)


    def _create_acl_rule(self, acl_name = "", acl_policy = True, mac_list = []):
        """
        This function adds a new ACL rule to the Access Controls table.
        Input:
        - acl_name: name of ACL rule
        - acl_policy: the bool value indicate the policy of particular ACL. If it's True, policy is allow-all.
        Otherwise, policy is deny-all.
        - mac_list: list of mac address added to an ACL rule.
        """
        ##zj 20140410 fixed ZF-8015
        if self.s.is_element_present(self.info['loc_cfg_acl_icon_expand']):
            pass
        elif self.s.is_element_present(self.info['loc_cfg_acl_icon_collapse']): 
            self.s.click_and_wait(self.info['loc_cfg_acl_icon_collapse']) 
        ##zj 20140410 fixed ZF-8015            

        self.s.click_and_wait(self.info['loc_cfg_acl_createnew_span'])
        self.s.type_text(self.info['loc_cfg_acl_name_textbox'], acl_name)
        if acl_policy:
            self.s.click_and_wait(self.info['loc_cfg_acl_allowall_radio'])

        else:
            self.s.click_and_wait(self.info['loc_cfg_acl_denyall_radio'])

        for mac in mac_list:
            self.s.type_text(self.info['loc_cfg_acl_mac_textbox'], mac)
            self.s.click_and_wait(self.info['loc_cfg_acl_createnew_station_button'])
            self.s.get_alert(self.info['loc_cfg_acl_cancel_button'])
            time.sleep(1)

        self.s.click_and_wait(self.info['loc_cfg_acl_ok_button'])
        self.s.get_alert(self.info['loc_cfg_acl_cancel_button'])


    def _delete_mac_addr_in_acl(self, mac_addr):
        """
        This function deletes a mac address within an ACL
        - mac_addr: mac address is deleted
        """
        i = 0
        total_entries = self.s.get_text(self.info['loc_cfg_acl_mac_table']).split('delete')[:-1]
        while i < len(total_entries):
            delete_mac = self.info['loc_cfg_acl_mac_delete_span']
            delete_mac = delete_mac.replace("$_$", str(i + 1))

            find_mac = self.info['loc_cfg_acl_mac_addr_cell']
            find_mac = find_mac.replace("$_$", str(i + 1))
            get_mac = self.s.get_text(find_mac)

            if get_mac == mac_addr:
                self.s.click_and_wait(delete_mac)
                break

            i += 1

    def _delete_all_mac_addrs_in_acl(self):
        """
        This function deletes all mac addresses within an ACL
        """
        i = 0
        total_entries = self.s.get_text(self.info['loc_cfg_acl_mac_table']).split('delete')[:-1]
        while i < len(total_entries):
            delete_mac = self.info['loc_cfg_acl_mac_delete_span']
            delete_mac = delete_mac.replace("$_$", str(i + 1))
            self.s.click_and_wait(delete_mac)
            i += 1

    def clone_acl_rule(self, old_acl_name, new_acl_name):
        """
        This function is used for cloning a acl
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_CONTROLS, 3)
        ##zj 20140410 fixed ZF-8015
        if self.s.is_element_present(self.info['loc_cfg_acl_icon_expand']):
            pass
        elif self.s.is_element_present(self.info['loc_cfg_acl_icon_collapse']): 
            self.s.click_and_wait(self.info['loc_cfg_acl_icon_collapse']) 
        ##zj 20140410 fixed ZF-8015                   
        total_acls = self._get_total_number(self.info['loc_cfg_total_acls_span'], "Access Controls")
        max_acls_row = int(self.info['const_cfg_max_acl_rows'])
        traverse_row = 1
        i = 0

        if total_acls == u'0':
            logging.info("There's no acl rules in the Access Controls table")
            return

        while i < int(total_acls):
            find_acl_name = self.info['loc_cfg_acl_name_cell']
            find_acl_name = find_acl_name.replace('$_$', str(traverse_row))
            get_acl_name = self.s.get_text(find_acl_name)

            if get_acl_name == old_acl_name:
                acl_edit = self.info['loc_cfg_acl_clone_span']
                acl_edit = acl_edit.replace('$_$', str(i))
                self.s.click_and_wait(acl_edit)

                if new_acl_name:
                    self.s.type_text(self.info['loc_cfg_acl_name_textbox'], new_acl_name)

                    self.s.click_and_wait(self.info['loc_cfg_acl_ok_button'])
                    self.s.get_alert(self.info['loc_cfg_acl_cancel_button'])
                    return

            if traverse_row == max_acls_row:
                traverse_row = 0
                self.s.click_and_wait(self.info['loc_cfg_acl_next_image'])

            traverse_row += 1
            i += 1
            time.sleep(1)

        logging.info("No ACL rule named %s existed in the ACL table" % old_acl_name)


    def edit_acl_rule(self, old_acl_name, new_acl_name = "", is_added_mac = False, mac_list = [],
                    is_modified_policy = False, new_policy = False, old_mac_addr = ""):
        """
        This function edits an existed acl rule
        Input:
        - old_acl_name: name of the existed acl
        - new_acl_name: new name of the edited acl
        - is_added_mac: the bool value determine whether mac addresses  are added or not
        - is_modify_policy: the bool value determine whether modify the current ACL rule or not
        - mac_list: list of added mac addresses
        - new_policy: new policy added to the ACL
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_CONTROLS, 5)

        ##zj 20140410 fixed ZF-8015
        if self.s.is_element_present(self.info['loc_cfg_acl_icon_expand']):
            pass
        elif self.s.is_element_present(self.info['loc_cfg_acl_icon_collapse']): 
            self.s.click_and_wait(self.info['loc_cfg_acl_icon_collapse']) 
        ##zj 20140410 fixed ZF-8015  

        #cwang@2010-9-30, checking element first, for scaling test.
        try:
            self._fill_search_txt(self.info['loc_cfg_l2_acl_search_textbox'], old_acl_name, is_refresh = False)
        except Exception, e:
            logging.debug(e.message)
            self._fill_search_txt(self.info['loc_cfg_l2_acl_search_textbox'], old_acl_name, is_refresh = True)

        try:

            if not self._wait_for_element(self.info['loc_cfg_total_acls_span'], is_refresh = True):
                raise Exception('Element [%s] not found' % self.info['loc_cfg_total_acls_span'])

            total_acls = self._get_total_number(self.info['loc_cfg_total_acls_span'], "Access Controls")
            max_acls_row = int(self.info['const_cfg_max_acl_rows'])
            traverse_row = 1
            i = 0

            if total_acls == u'0':
                logging.info("There's no acl rules in the Access Controls table")
                return

            while i < int(total_acls):
                find_acl_name = self.info['loc_cfg_acl_name_cell']
                find_acl_name = find_acl_name.replace('$_$', str(traverse_row))
                get_acl_name = self.s.get_text(find_acl_name)

                if get_acl_name == old_acl_name:
                    acl_edit = self.info['loc_cfg_acl_edit_span']
                    acl_edit = acl_edit.replace('$_$', str(i))
                    self.s.click_and_wait(acl_edit)

                    if new_acl_name:
                        self.s.type_text(self.info['loc_cfg_acl_name_textbox'], new_acl_name)
                    if is_added_mac:
                        if len(mac_list) == 1:
                            self._delete_mac_addr_in_acl(old_mac_addr)
                            self.s.type_text(self.info['loc_cfg_acl_mac_textbox'], mac_list[0])
                            self.s.click_and_wait(self.info['loc_cfg_acl_createnew_station_button'])
                            self.s.get_alert(self.info['loc_cfg_acl_cancel_button'])

                        else:
                            self._delete_all_mac_addrs_in_acl()
                            for mac in mac_list:
                                self.s.type_text(self.info['loc_cfg_acl_mac_textbox'], mac)
                                self.s.click_and_wait(self.info['loc_cfg_acl_createnew_station_button'])
                                self.s.get_alert(self.info['loc_cfg_acl_cancel_button'])
                                time.sleep(1)

                    if is_modified_policy:
                        if new_policy:
                            self.s.click_and_wait(self.info['loc_cfg_acl_allowall_radio'])
                        else:
                            self.s.click_and_wait(self.info['loc_cfg_acl_denyall_radio'])

                    self.s.click_and_wait(self.info['loc_cfg_acl_ok_button'])
                    self.s.get_alert(self.info['loc_cfg_acl_cancel_button'])

                    return


                if traverse_row == max_acls_row:
                    traverse_row = 0
                    self.s.click_and_wait(self.info['loc_cfg_acl_next_image'])
                traverse_row += 1
                i += 1
                time.sleep(1)

            logging.info("No ACL rule named %s existed in the ACL table" % old_acl_name)

        finally:
            self._fill_search_txt(self.info['loc_cfg_l2_acl_search_textbox'], '')
            
    def renew_entitlement(self, file_path):
        self.navigate_to(self.ADMIN, self.ADMIN_SUPPORT, 3)
        
        if not self.s.is_element_present(self.info['loc_admin_check_entitlement_button']):
            logging.info("this release[%s] doesn't support entitlement" % self.version.get('release'))
            return
        
        no_entitlement_alert = self.info['loc_admin_no_entitlement_alert_text']
        if not self.s.is_element_visible(no_entitlement_alert) or \
            "A support upgrade entitlement does not appear" not in self.s.get_text(no_entitlement_alert):
            logging.info("there is a valid entitlement, no need to renew it")
            return
        
        entitlement_file = self.mac_addr.replace(':', '')+'.spt'
        entitlement_file = file_path+"\\"+entitlement_file
        logging.info("the entitlement file is [%s]" % entitlement_file)
        
        entitlement_import_button = self.info['loc_admin_browse_entitlement_file_button']
        if not self.s.is_element_present(entitlement_import_button):
            raise Exception("Element %s not found" % entitlement_import_button)
        
        if self.browser_type == "ie":
            dlg = StandardDialog(StandardDialog.IE_CHOOSE_FILE_DLG, entitlement_file)
            manager = DialogManager()
            manager.add_dialog(dlg)
            manager.start()
            self.s.click_and_wait(entitlement_import_button)
            manager.join(10)
            manager.shutdown()
        else:
            try:
                self.s.type_text(entitlement_import_button, entitlement_file)
            except:
                raise Exception("Can not set value %s to the locator %s" % (entitlement_file, entitlement_import_button))
        
        entitlement_perform_button = self.info['loc_admin_perform_entitlement_upload_button']
        if not self.s.is_element_visible(entitlement_perform_button):
            raise Exception("Element %s not found" % entitlement_perform_button)
        else:
            self.s.click_and_wait(entitlement_perform_button)
            if not self.s.is_element_visible(self.info['loc_admin_entitlement_table']):
                raise Exception("upload entitlement file failed, because element %s not found" % self.info['loc_admin_entitlement_table'])
            else:
                logging.info("upload entitlement file successfully")
        
        return
        
    def remove_all_acl_rules(self):
        """
        Remove all ACL rules out of the Access Controls table
        """
        AC.delete_all_l2_acl_policies(self)
        AC.delete_all_l3_acl_policies(self)
        AC.delete_all_l3_ipv6_acl_policies(self)

    def _remove_all_acl_rules(self):
        """
        Remove about 200 ACL rules out of the Access Controls table
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_CONTROLS, 3)
        max_acls_row = int(self.info['const_cfg_max_acl_rows'])

        delete_entries = 0
        total_acl = 1
        while delete_entries < 200 and total_acl > 0:
            if not self.s.is_checked(self.info['loc_cfg_acl_all_checkbox']):
                time.sleep(2)
                self.s.click_and_wait(self.info['loc_cfg_acl_all_checkbox'], 4)

            self.s.choose_ok_on_next_confirmation()
            self.s.click_and_wait(self.info['loc_cfg_acl_delete_button'], 4)
            if self.s.is_confirmation_present(5):
                self.s.get_confirmation()

            delete_entries += max_acls_row

            time.sleep(3)
            total_acl = int(self._get_total_number(self.info['loc_cfg_total_acls_span'], "Access Controls"))
            time.sleep(3)

        return total_acl


    def _remove_known_rogue_ap(self):
        total_rogue_dev = self._get_total_number(self.info['loc_mon_total_known_rogue_devices_span'], "Know Rogue Devices")
        if total_rogue_dev == u'0':
            logging.info("The known rogue devices table is empty")

        else:
            while True:
                self._delete_element(self.info['loc_mon_roguedevices_knownrogue_all_checkbox'],
                                     self.info['loc_mon_roguedevices_knownrogue_delete_button'],
                                     "all known Rogue Devices")

                total_rogue_dev = self._get_total_number(self.info['loc_mon_total_known_rogue_devices_span'],
                                                         "Know Rogue Devices")
                time.sleep(2)
                if total_rogue_dev != u'0':
                    continue

                break

    def _mark_rogue_ap(self):
        total_rogue_dev = self._get_total_number(self.info['loc_mon_total_rogue_devices_span'], "Rogue Devices")
        if total_rogue_dev == u'0':
            logging.info("The rogue devices table is empty")

        else:
            for i in range(int(total_rogue_dev)):
                locator = self.info['loc_mon_roguedevices_action_cell']
                self.s.click_and_wait(locator, 2)
                if i == 10:
                    break


    def set_country_code(self, country_code = "", optimize=None, allow_indoor =None,set_country_code=True):
        """
        Change country code on the ZoneDirector
        Input:
        - country_code: name of country code
        """
        logging.info('ready to set country to %s'%country_code)
        optimize_option={'compatibility'    :r'//input[@id="opt-cmptb"]',
                         'Interoperability' :r'//input[@id="opt-intprb"]',
                         'Performance'      :r'//input[@id="opt-perf"]',
                         }
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)

        cc = self.info['loc_cfg_sys_ctrycode_option']
        if set_country_code:
            # If the input parameter country_code is null, use random country code to set for the ZD
            if not country_code:
                time.sleep(3)
                cc_list = self.s.get_select_options(cc)
                while True:
                    country_code = cc_list[random.randint(0, len(cc_list) - 1)]
                    # If random country code is the same as the current country code, continue select other one
                    if country_code == self.s.get_selected_label(cc) or country_code == "Slovakia (Slovak Republic)":
                        continue
                    else:
                        break
            country_code=country_code.strip()
            all_ctry = self.s.get_select_options(cc)
            if country_code not in all_ctry:
                country_code = country_code.capitalize()
            if country_code not in all_ctry:
                msg = ('no conutry code(%s) can be selected in [%s]'%(country_code,all_ctry))
                logging.error(msg)
                raise Exception(msg) 
            self.s.select_option(cc,country_code)
            logging.info('select country %s successfully'%country_code)
            
        if optimize and self.s.is_element_present(optimize_option[optimize]):
            self.s.click(optimize_option[optimize])
            
        if allow_indoor is not None and self.s.is_element_present(self.info['loc_cfg_sys_allow_indoor_channel']):
            if allow_indoor:
                self.s.click_if_not_checked(self.info['loc_cfg_sys_allow_indoor_channel'])
            else:
                self.s.click_if_checked(self.info['loc_cfg_sys_allow_indoor_channel'])
            
        self.s.choose_ok_on_next_confirmation()
        self.s.click_and_wait(self.info['loc_cfg_sys_ctrycode_apply_button'])
        if not self.s.is_confirmation_present(5):
            raise Exception("No dialog confirmation for setting country code appeared")
        self.s.get_confirmation()
        logging.info("Change country code for ZoneDirector to %s successfully" % country_code)


    def get_country_code(self):
        """
        Get the current name of country code
        Input: none
        Output: return a dictionary with 2 keys:
        - label: name of country code, ex: United States, United Kingdom
        - value: value of country code, ex: US, UK
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)

        cc = self.info['loc_cfg_sys_ctrycode_option']
        if not self.s.is_element_present(cc):
            raise Exception("Element %s not found" % cc)

        time.sleep(1)
        country_code = {}
        country_code['label'] = self.s.get_selected_label(cc)
        country_code['value'] = self.s.get_value(cc)

        return country_code

    #cwang@2010-10-14, append is_refresh.
    def _wait_for_element(self, locator, timeout = 20, is_refresh = False):
        end_t = time.time()
        while time.time() - end_t < timeout * 3:
            if self.s.is_element_present(locator) and self.s.is_visible(locator):
                return True
            if is_refresh:
                try:
                    self.refresh()
                except:
                    pass
            time.sleep(timeout)

        return False

    def _get_total_number(self, locator, table_name):
        """
        """
        total = self.s.get_text(locator)
        if not total:
            self.refresh()
            time.sleep(10)
            total = self.s.get_text(locator)

        pat1 = ".*\(([0-9]+)\)$"
        match_obj1 = re.search(pat1, total)
        
        #if the current page include all the items, the total number will like this '1-3(3)'
        pat2 = "(\d+)-(\d+) \((\d+)\)"
        match_obj2 = re.search(pat2, total)
        
        if match_obj1:
            total = match_obj1.group(1)
        elif match_obj2:
            total = match_obj2.group(3)
        else:
            raise Exception("Can not get the total number of rows in %s table" % table_name)

        return total


    def _delete_element(self, checkbox, del_button, element_name):
        """
        This function is used to delete an element in the stable way by checking if the element presents or not,
        get dialog confirmation when removing the element.
        Input:
        - Checkbox: used to specify the element locator
        - del_button:
        - element_name: name of the deleting element.
        """
        if not self.s.is_checked(checkbox):
            self.s.click_and_wait(checkbox)

        self.s.choose_ok_on_next_confirmation()
        self.s.click_and_wait(del_button)

        time.sleep(1)
        if not self.s.is_confirmation_present(5):
            raise Exception("No dialog confirmation for deleting %s appears on checkbox(%s)/del_button(%s)" % (element_name, checkbox, del_button))

        self.s.get_confirmation()
        
        alt = self.s.get_alert()
        if alt:
            logging.info('alert get %s'%alt)
            raise Exception('alert get [%s]'%alt)
        


    def goto_login_page(self):
        '''
        '''
        self.do_login()


    def do_login(self):
        self.s.open(self.conf['url.login'])
        self.login()


    def login(self, force = False):
        WebUI.login(self, force)

    def _set_wlan_auth_method(self, auth, auth_server_name = "", use_web_auth = False, use_guest_access = False):
        """
        Configure authentication method for a WLAN

        Input:
        - auth: authentication method("open", "shared" or "EAP")
        - auth_server_name: name of authentication server if 802.1x-EAP is used.
        Default is NULL, which means that 802.1x-EAP uses the local database
        - use_web_auth: if it's True, enable web authentication feature. Otherwise, disable this feature
        - use_guest_access: If it's True, enable guest access feature. Otherwise, disable this feature
        Output: none
        """
        if (auth == self.info['const_auth_method_open']):
            a = self.info['loc_cfg_open_radio']
            self.s.click_and_wait(a)
            if use_guest_access:
                if not self.s.is_checked(self.info['loc_cfg_wlans_usage_guest_checkbox']):
                    self.s.click_and_wait(self.info['loc_cfg_wlans_usage_guest_checkbox'])

        elif (auth == self.info['const_auth_method_shared']):
            a = self.info['loc_cfg_shared_radio']
            self.s.click_and_wait(a)

        else:
            a = self.info['loc_cfg_eap_radio']
            self.s.click_and_wait(a)
            if auth_server_name:
                # Choose authentication database for 802.1x-eap
                auth_server = self.info['loc_cfg_auth_server_eap_select']
                self.s.select_option(auth_server, auth_server_name)

        if  (auth != self.info['const_auth_method_eap']):
            if use_web_auth and not use_guest_access:
                if not self.s.is_checked(self.info['loc_cfg_web_auth_checkbox']):
                    self.s.click_and_wait(self.info['loc_cfg_web_auth_checkbox'])

                if auth_server_name:
                    self.s.select_option(self.info['loc_cfg_auth_server_web_select'], auth_server_name)

    def _set_wlan_encryption_none(self, auth):
        """
        Configure a WLAN with no encryption
        Input:
        - auth: authentication method that does not need encryption
        Output: none
        """
        if(auth != self.info['const_auth_method_open']):
            self.s.click_and_wait(self.info['loc_cfg_open_radio'])

        self.s.click_and_wait(self.info['loc_cfg_none_radio'])


    def _set_wlan_encryption_wpa(self, wpa_ver, auth, encryption, key_string = ""):
        """
        Configure encryption method for WLAN if WPA is used
        Input:
        - wpa_ver: WPA/WPA2
        - auth: an authentication method(open/802.1x EAP) that supports WPA/WPA2 encryption
        - encryption: an encryption method that WPA/WPA2 uses to encrypt data (TKIP/AES)
        - key_string: also called passphrase
        Output: none
        """
        if((auth == self.info['const_auth_method_open']) or (auth == self.info['const_auth_method_eap'])):
            if ((wpa_ver == self.info['const_encryption_method_wpa']) or (wpa_ver == self.info['const_encryption_method_wpa2'])):
                if(wpa_ver == self.info['const_encryption_method_wpa']):
                    if not self.s.is_element_present(self.info['loc_cfg_wpa_radio']):
                        raise Exception("Element %s not found" % self.info['loc_cfg_wpa_radio'])

                    a = self.info['loc_cfg_wpa_radio']

                else:
                    if not self.s.is_element_present(self.info['loc_cfg_wpa2_radio']):
                        raise Exception("Element %s not found" % self.info['loc_cfg_wpa2_radio'])

                    a = self.info['loc_cfg_wpa2_radio']

                self.s.click_and_wait(a)

                # Set encryption algorithm to TKIP or AES
                if (encryption == self.info['const_algorithm_tkip']):
                    if not self.s.is_element_present(self.info['loc_cfg_tkip_radio']):
                        raise Exception("Element %s not found" % self.info['loc_cfg_tkip_radio'])

                    b = self.info['loc_cfg_tkip_radio']

                elif (encryption == self.info['const_algorithm_aes']):
                    if not self.s.is_element_present(self.info['loc_cfg_aes_radio']):
                        raise Exception("Element %s not found" % self.info['loc_cfg_aes_radio'])

                    b = self.info['loc_cfg_aes_radio']

                self.s.click_and_wait(b)

        # Only authentication method Open supports key_string
        if (auth == self.info['const_auth_method_open']):
            self.s.type_text(self.info['loc_cfg_passphrase_textbox'], key_string)


    def _set_wlan_encryption_wep(self, auth, wep_method, key_index, key_string = ""):
        """
        Configure encryption method for WLAN to WEP-64/WEP-128
        Input:
        - auth: an authentication method that supports WEP-64/WEP-128 encryption
        - wep_method: WEP-64 or WEP-128
        - key_index: WEP key index
        - key_string: WEP key
        Output: none
        """
        # Only Open and Shared require WEP Key
        if((auth == self.info['const_auth_method_open']) or (auth == self.info['const_auth_method_shared'])):
            if (wep_method == self.info['const_encryption_method_wep64']) or \
                (wep_method == self.info['const_encryption_method_wep128']):

                if (wep_method == self.info['const_encryption_method_wep64']):
                    if not self.s.is_element_present(self.info['loc_cfg_wep64_radio']):
                        raise Exception("Element %s not found" % self.info['loc_cfg_wep64_radio'])
                    a = self.info['loc_cfg_wep64_radio']

                else:
                    if not self.s.is_element_present(self.info['loc_cfg_wep128_radio']):
                        raise Exception("Element %s not found" % self.info['loc_cfg_wep128_radio'])
                    a = self.info['loc_cfg_wep128_radio']

                self.s.click_and_wait(a)

                for index in range(4):
                    if key_index == self.info["const_wep_index" + str(index + 1)]:
                        b = self.info["loc_cfg_wepkey_index" + str(index + 1) + "_radio"]
                        if not self.s.is_element_present(b):
                            raise Exception("Element %s not found" % b)

                        self.s.click_and_wait(b)

                        break

                # Click Generate button if key_string is blank
                if key_string == "":
                    self.s.click_and_wait(self.info['loc_cfg_generate_wep_button'])

                else:
                    self.s.type_text(self.info['loc_cfg_wepkey_textbox'], key_string)

        # 802.1x-eap doesn't support WEP key
        elif (auth == self.info['const_auth_method_eap']):
            if (wep_method == self.info['const_encryption_method_wep64']):
                if not self.s.is_element_present(self.info['loc_cfg_wep64_radio']):
                    raise Exception("Element %s not found" % self.info['loc_cfg_wep64_radio'])

                a = self.info['loc_cfg_wep64_radio']

            elif (wep_method == self.info['const_encryption_method_wep128']):
                if not self.s.is_element_present(self.info['loc_cfg_wep128_radio']):
                    raise Exception("Element %s not found" % self.info['loc_cfg_wep128_radio'])

                a = self.info['loc_cfg_wep128_radio']

            self.s.click_and_wait(a)


    def _set_wlan_advanced_option(self, acl_name = "", use_hide_ssid = False, vlan_id = "",
                                  uplink_rate_limit = "", downlink_rate_limit = "", do_tunnel = False):
        """
        This function is used to set advanced options for particular wlan. These options can be acl, rate-limit,
        vlan, hide ssid for beacon broadcasting.
        Input:
        - acl_name: name of acl. If it's null, the wlan does not use acl
        - use_hide_ssid: determine if hide ssid in beacon broadcasting or not
        - vlan_id: id of particular vlan
        - use_rate_limit: determine whether using rate-limit or not
        - uplink_rate: set uplink rate for wlan which enabled rate-limit feature
        - downlink_rate: set downlink rate for wlan which enable rate-limit feature
        - do_tunnel: Enable tunnel mode if True, disable if False
        """
        self.s.click_and_wait(self.info['loc_cfg_wlans_advanced_options_anchor'])
        if acl_name:
            self.s.select_option(self.info['loc_cfg_wlans_acl_option'], acl_name)

        if uplink_rate_limit:
            self.s.select_option(self.info['loc_cfg_wlans_uplink_preset_option'], uplink_rate_limit)

        if downlink_rate_limit:
            self.s.select_option(self.info['loc_cfg_wlans_downlink_preset_option'], downlink_rate_limit)

        if vlan_id:
            if self.s.is_element_present(self.info['loc_cfg_wlans_do_vlan_checkbox']):    
                self.s.click_and_wait(self.info['loc_cfg_wlans_do_vlan_checkbox'])
            self.s.type(self.info['loc_cfg_wlans_vlan_id_textbox'], vlan_id)

        if use_hide_ssid:
            self.s.click_if_not_checked(self.info['loc_cfg_wlans_do_beacon_checkbox'])

        if do_tunnel:
            if not self.s.is_visible(self.info['loc_cfg_wlans_do_tunnel_checkbox']):
                raise Exception("Not found tunnel option. Maybe mobility license has not imported.")

            if not self.s.is_checked(self.info['loc_cfg_wlans_do_tunnel_checkbox']):
                self.s.click_and_wait(self.info['loc_cfg_wlans_do_tunnel_checkbox'])

        else:
            if self.s.is_visible(self.info['loc_cfg_wlans_do_tunnel_checkbox']):
                if self.s.is_checked(self.info['loc_cfg_wlans_do_tunnel_checkbox']):
                    self.s.click_and_wait(self.info['loc_cfg_wlans_do_tunnel_checkbox'])


    def _create_wlan(self, ssid, auth = "", encryption = "", wpa_ver = "", key_string = "",
                     key_index = "", auth_server_name = "", use_web_auth = False, use_guest_access = False,
                     acl_name = "", hide_ssid = False, vlan_id = "", uplink_rate_limit = "",
                     downlink_rate_limit = "", use_client_isolation = False, use_zero_it = False,
                     use_dynamic_psk = False, do_tunnel = False):
        """
        Create a wlan using input paramters
        Input: refer to the following functions to see the definition of input parameters: _set_wlan_auth_method,
        _set_wlan_encryption_none, _set_wlan_encryption_wpa, _set_wlan_encryption_wep
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS)
        
        self.s.click_and_wait(self.info['loc_cfg_wlan_create_span'])
        s_t = time.time()
        while time.time() - s_t < 30:
            if self.s.is_element_visible(self.info['loc_cfg_ssid_name_textbox']):
                break
            else:
                self.refresh()
                self.s.click_and_wait(self.info['loc_cfg_wlan_create_span'])
                time.sleep(2)

        self.s.type_text(self.info['loc_cfg_ssid_name_textbox'], ssid)

        #cwang@2010-11-1, behavior change after Toranto 9.1.0.0.7
        if self.s.is_element_visible(self.info['loc_cfg_ssid_textbox']):
            self.s.type_text(self.info['loc_cfg_ssid_textbox'], ssid)

        self._set_wlan_auth_method(auth, auth_server_name, use_web_auth, use_guest_access)

        if encryption == self.info['const_encryption_method_none']:
            self._set_wlan_encryption_none(auth)

        elif encryption == self.info['const_algorithm_tkip'] or encryption == self.info['const_algorithm_aes']:
            self._set_wlan_encryption_wpa(wpa_ver, auth, encryption, key_string)

        elif encryption == self.info['const_encryption_method_wep64'] or encryption == self.info['const_encryption_method_wep128']:
            self._set_wlan_encryption_wep(auth, encryption, key_index, key_string)

        if use_client_isolation:
            self.s.click_if_not_checked(self.info['loc_cfg_client_isolation_checkbox'])

        if use_zero_it:
            self.s.click_if_not_checked(self.info['loc_cfg_wlans_zero_it_activation_checkbox'])
            if use_dynamic_psk:
                self.s.click_if_not_checked(self.info['loc_cfg_wlans_dynamic_psk_checkbox'])

        # Set advanced options for this wlan if applicable
        self._set_wlan_advanced_option(acl_name, hide_ssid, vlan_id, uplink_rate_limit, downlink_rate_limit, do_tunnel)
        self.s.click_and_wait(self.info['loc_cfg_wlan_ok_button'])

        # If an alert of wrong configuration(ex: wrong wlan name, duplicated name...) appears,
        # click the Cancel button
        self.s.get_alert(self.info['loc_cfg_wlan_cancel_button'])
        logging.info("Create wlan " + ssid + " successfully")

    def _delete_wlan(self, ssid):
        """ Remove a Wlan out of Wlans Table
        Input:
        - ssid: name of the wlan to be deleted
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS)

        wlan_count = 0
        while True:
            wc = self.info['loc_cfg_wlan_row']
            wc = wc.replace("$_$", str(wlan_count))
            if not self.s.is_element_present(wc):
                break

            wlan_count = wlan_count + 1

        if wlan_count == 0:
            return

        for wlan_row in range(wlan_count):
            find_wlan = self.info['loc_cfg_wlan_cell']
            find_wlan = find_wlan.replace("$_$", str(wlan_row + 1))
            checkbox = self.info['loc_cfg_wlan_checkbox']
            checkbox = checkbox.replace("$_$", str(wlan_row + 1))
            get_ssid = self.s.get_text(find_wlan)

            if get_ssid == ssid:
                self._delete_element(checkbox, self.info['loc_cfg_wlan_delete_button'], "wlan")
                if (self.s.is_alert_present(5)):
                    msg_alert = self.s.get_alert()
                    raise Exception(msg_alert)

                logging.info("Delete wlan " + ssid + " successfully")

                return

            else:
                wlan_row += 1

        logging.info("Wlan " + ssid + " is not existed in the wlan table")


    def _delete_all_wlan(self):
        """
        Remove all wlans out of WLANs table
        Input: none
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS, force = True)

        if not self.s.is_element_present(self.info['loc_cfg_wlan_check_first_row']):
            logging.info("No wlans existed in the wlan table")
            return

        a = self.info['loc_cfg_wlan_check_all_checkbox']
        self._delete_element(a, self.info['loc_cfg_wlan_delete_button'], "all wlans")
        if (self.s.is_alert_present(5)):
            msg_alert = self.s.get_alert()
            raise Exception(msg_alert)

        logging.info("Delete all wlans successfully")


    def _create_radius_server(self, ras_addr, ras_port, ras_secret, server_name = ""):
        """
        Create a radius authentication server

        Input:
        - ras_addr: ip address(also the name) of authentication server.
        - ras_port: port on which the server is listening
        - ras_secret: a secret password, shared between server and client.
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER)
        self.s.click_and_wait(self.info['loc_cfg_authsvr_create_new_span'])
        tmp_name = ""
        if server_name:
            tmp_name = server_name
            self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], server_name)

        else:
            tmp_name = ras_addr
            self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], ras_addr)

        self.s.type_text(self.info['loc_cfg_authsvr_ip_address_textbox'], ras_addr)

        self.s.click_and_wait(self.info['loc_cfg_authsvr_type_radius_radio'])

        # If radius server port is different from the default
        if ras_port != self.info['const_radius_default_port']:
            self.s.type_text(self.info['loc_cfg_authsvr_port_textbox'], ras_port)

        self.s.type_text(self.info['loc_cfg_authsvr_pwd_textbox'], ras_secret)
        self.s.type_text(self.info['loc_cfg_authsvr_pwd2_textbox'], ras_secret)
        self.s.click_and_wait(self.info['loc_cfg_authsvr_ok_button'])

        # If an alert of wrong configuration(ex: wrong server name, duplicated name) appears
        # click the Cancel button
        self.s.get_alert(self.info['loc_cfg_authsvr_cancel_button'])
        logging.info("Server " + tmp_name + " is created successfully")


    def _delete_radius_server(self, ras_addr):
        """
        Remove a Server out of Authentication Server Table

        Input:
        - ras_name: name of the server to be deleted
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER)
        auth_serv_total = self._get_total_number(self.info['loc_cfg_authsvr_total_number_span'], "Authentication Servers")

        # If no users existed, return immediately
        if auth_serv_total == u"0":
            logging.info("No authentication server existed in the table")
            return

        max_auth_serv_row = int(self.info['const_cfg_authsvr_table_size'])
        row = 1
        i = 0
        # Find server's name on the authentication server table
        while i < int(auth_serv_total):
            find_serv = self.info['loc_cfg_authsvr_name_cell']
            find_serv = find_serv.replace("$_$", str(row))
            checkbox = self.info['loc_cfg_authsvr_select_checkbox']
            checkbox = checkbox.replace("$_$", str(row))
            get_ras_addr = self.s.get_text(find_serv)

            if get_ras_addr == ras_addr:
                self._delete_element(checkbox, self.info['loc_cfg_authsvr_delete_button'], "authentication server")
                logging.info("Delete authentication server " + ras_addr + " successfully")
                return

            if row == max_auth_serv_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_authsvr_next_image'])

            row = row + 1
            i = i + 1
            time.sleep(1)

        logging.info("Authentication server " + ras_addr + " does not exist in the table")


    def _delete_all_auth_server(self):
        """
        Remove all servers out of Authentication Server Table

        Input: none
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER, 2)

        while (True):
            auth_serv_total = self._get_total_number(self.info['loc_cfg_authsvr_total_number_span'], "Authentication Servers")
            if auth_serv_total != "0":
                a = self.info['loc_cfg_authsvr_select_all_checkbox']
                self._delete_element(a, self.info['loc_cfg_authsvr_delete_button'], "all authentication servers")
                time.sleep(3)

            else:
                break

    def _create_ad_server(self, ad_addr, ad_port, ad_domain, server_name = ""):
        """
        Create a active directory authentication server

        Input:
        - ad_addr: ip address(also the name) of authentication server.
        - ad_port: port on which the server is listening
        - ad_domain:
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER)
        self.s.click_and_wait(self.info['loc_cfg_authsvr_create_new_span'])
        tmp_name = ""
        if server_name:
            tmp_name = server_name
            self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], server_name)

        else:
            tmp_name = ad_addr
            self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], ad_addr)

        self.s.type_text(self.info['loc_cfg_authsvr_ip_address_textbox'], ad_addr)

        self.s.click_and_wait(self.info['loc_cfg_authsvr_type_ad_radio'])

        # If radius server port is different from the default
        if ad_port != self.info['const_ad_default_port']:
            self.s.type_text(self.info['loc_cfg_authsvr_port_textbox'], ad_port)

        self.s.type_text(self.info['loc_cfg_authsvr_domain_textbox'], ad_domain)
        self.s.click_and_wait(self.info['loc_cfg_authsvr_ok_button'])

        # If an alert of wrong configuration(ex: wrong server name, duplicated name) appears
        # click the Cancel button
        self.s.get_alert(self.info['loc_cfg_authsvr_cancel_button'])
        logging.info("Server " + tmp_name + " is created successfully")


    def _create_user (self, username, password, fullname = '', role = 'Default', is_config_user_page = False):
        """
        Add a new user to the local database

        Input:
        - username:
        - password:
        - fullname:
        Output: none
        """
        if not is_config_user_page:
            self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS)

        self.s.click_and_wait(self.info['loc_cfg_user_create_span'])

        self.s.type_text(self.info['loc_cfg_username_textbox'], username)

        if fullname:
            self.s.type_text(self.info['loc_cfg_fullname_textbox'], fullname)

        self.s.type_text(self.info['loc_cfg_password_textbox'], password)
        self.s.type_text(self.info['loc_cfg_confirm_password_textbox'], password)
        if role != 'Default':
            self.s.select_option(self.info['loc_cfg_user_role_select'], role)

        self.s.click_and_wait(self.info['loc_cfg_user_ok_button'])

        # If an alert of wrong configuration(ex: wrong user name, duplicated name...) appears
        # click the Cancel button
        alt = self.s.get_alert(self.info['loc_cfg_user_cancel_button'])
        if alt:
            raise Exception(alt)
        logging.info("Create user " + username + " successfully")

        
    #Jacky.Luh update by 2012-06-26
    def wait_aps_join_in_zd_with_the_expect_status(self, ap_mac_list, ap_sym_dict):
        ap_upgrade_timeout = 900
        ap_connected_start_time = time.time()
        tb_ap_sym_dict = dict()
        tb_ap_mac_list = list()
        tb_ap_sym_dict.update(ap_sym_dict)
        tb_ap_mac_list = ap_mac_list
        for reconnected_ap in tb_ap_mac_list:
            for syms_ap in tb_ap_sym_dict.keys():
                if reconnected_ap == tb_ap_sym_dict[syms_ap]['mac']:
                    logging.info("The ap[%s] expected status is '%s'" % (reconnected_ap, 
                                                                         tb_ap_sym_dict[syms_ap]['status']))
            while(True):
                status = None
                sym_ap_status = None
                if (time.time() - ap_connected_start_time) > ap_upgrade_timeout:
                    logging.info("ap rejoin in zd failed with time out.")
                    return False
                self.click_mon_apsummary_refresh()
                status = self._get_ap_info(reconnected_ap)['status']
                self.click_mon_apsummary_refresh()
                for sym_ap in tb_ap_sym_dict.keys():                        
                    if reconnected_ap == tb_ap_sym_dict[sym_ap]['mac']:
                        sym_ap_status = tb_ap_sym_dict[sym_ap]['status']
                        if ' (' in status and ' (' in sym_ap_status:
                            if status.lower() == sym_ap_status.lower():
                                logging.info("The ap[%s] join in zd" % reconnected_ap)
                                break
                        else:
                            if status.lower().startswith(u"connected"):
                                logging.info("The ap[%s] join in zd" % reconnected_ap)
                                break                              
                    
                if ' (' in status and ' (' in sym_ap_status and status.lower() == sym_ap_status.lower():
                    break
                elif ' (' not in status and ' (' in sym_ap_status and status.lower().startswith(u"connected"):
                    break
                elif ' (' in status and ' (' not in sym_ap_status and status.lower().startswith(u"connected"):
                    break
                elif ' (' not in status and ' (' not in sym_ap_status and status.lower().startswith(u"connected"):
                    break
                else:
                    pass
            
        return True         
        

#added by west.li
#edit an exist user
    def edit_user(self, oldusername, newusername, password='', fullname = ""):
        """
        edit an exist user
        """
        self._edit_user(oldusername, newusername, password, fullname)

    def _edit_user (self, oldusername, newusername,password, fullname = '', is_config_user_page = False):
        """
        Add a new user to the local database

        Input:
        - oldusername:
        - newusername:
        - password:
        - fullname:
        Output: none
        """
        if not is_config_user_page:
            self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS)
            
        self._fill_search_txt(self.info['loc_cfg_user_search_textbox'], oldusername)

        user_total = self._get_total_number(self.info['loc_cfg_user_total_number_span'], "Users")
        # If no users existed, return immediately
        if user_total == u"0":
            logging.info("There's no users existed in the Users table to edit")
            return
        

        max_user_row = int(self.info['const_cfg_max_row_user'])
        row = 1
        i = 0
        # Find user's name on the user table
        while i < int(user_total):
            find_user = self.info['loc_cfg_user_row']
            find_user = find_user.replace("$_$", str(row))
            edit = self.info['loc_cfg_user_edit_apan']
            edit = edit.replace("$_$", str(i))
            get_username = self.s.get_text(find_user)

            if get_username == oldusername:
                self.s.click_and_wait(edit)
                if newusername:
                    self.s.type_text(self.info['loc_cfg_username_textbox'], newusername)

                if fullname:
                    self.s.type_text(self.info['loc_cfg_fullname_textbox'], fullname)
                if password:
                    self.s.type_text(self.info['loc_cfg_password_textbox'], password)
                    self.s.type_text(self.info['loc_cfg_confirm_password_textbox'], password)
                self.s.click_and_wait(self.info['loc_cfg_user_ok_button'])
                alt = self.s.get_alert(self.info['loc_cfg_user_cancel_button'])
                if alt:
                    raise Exception(alt)

                return

            if row == max_user_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_user_next_image'])

            row = row + 1
            i = i + 1
            time.sleep(1)

    def get_user(self):
        """
        Get all user from the Users table
        Output: returns a list of users
        """

        self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS)

        user_total = self._get_total_number(self.info['loc_cfg_user_total_number_span'], "Users")
        user_list = []
        row = 1
        i = 0
        max_row_user = int(self.info['const_cfg_max_row_user'])
        if user_total == u'0':
            logging.info("The Users table is empty")
            return []

        while i < int(user_total):
            username = self.info['loc_cfg_user_name_cell']
            username = username.replace("$_$", str(i))
            get_username = self.s.get_text(username)
            user_list.append(get_username)
            if row == max_row_user:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_user_next_image'], 2)

            row = row + 1
            i = i + 1

        return user_list


    def clone_user(self, old_username, new_username, password, fullname = ""):
        """
        """
        self._clone_user(old_username, new_username, password, fullname = "")


    def _clone_user(self, old_username, new_username, password, fullname = ""):
        """
        Edit an existed User
        Input:
        - old_username: old name of modified user
        - new_username: new name of modified user
        - password: new password of modified user
        - fullname: Fullname of modified user. Default is null
        """
        # Navigate to Tab Configure and menu Users
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS)

        user_total = self._get_total_number(self.info['loc_cfg_user_total_number_span'], "Users")
        # If no users existed, return immediately
        if user_total == u"0":
            logging.info("There's no users existed in the Users table to clone")
            return

        max_user_row = int(self.info['const_cfg_max_row_user'])
        row = 1
        i = 0
        # Find user's name on the user table
        while i < int(user_total):
            find_user = self.info['loc_cfg_user_row']
            find_user = find_user.replace("$_$", str(row))
            clone = self.info['loc_cfg_user_clone_apan']
            clone = clone.replace("$_$", str(i))
            get_username = self.s.get_text(find_user)

            if get_username == old_username:
                self.s.click_and_wait(clone)
                if new_username:
                    self.s.type_text(self.info['loc_cfg_username_textbox'], new_username)

                if fullname:
                    self.s.type_text(self.info['loc_cfg_fullname_textbox'], fullname)

                self.s.type_text(self.info['loc_cfg_password_textbox'], password)
                self.s.type_text(self.info['loc_cfg_confirm_password_textbox'], password)
                self.s.click_and_wait(self.info['loc_cfg_user_ok_button'])
                self.s.get_alert(self.info['loc_cfg_user_cancel_button'])

                return

            if row == max_user_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_user_next_image'])

            row = row + 1
            i = i + 1
            time.sleep(1)


    def _delete_user(self, username):
        """
        Remove a user out of the local database

        Input:
        - username:
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS)
        self._fill_search_txt(self.info['loc_cfg_user_search_textbox'], username)

        user_total = self._get_total_number(self.info['loc_cfg_user_total_number_span'], "Users")
        # If no users existed, return immediately
        if user_total == u"0":
            logging.info("There's no users existed in the Users table to delete")
            return

        max_user_row = int(self.info['const_cfg_max_row_user'])
        row = 1
        # Find user's name on the user table
        for user_row in range(int(user_total)):
            find_user = self.info['loc_cfg_user_row']
            find_user = find_user.replace("$_$", str(row))
            checkbox = self.info['loc_cfg_user_checkbox']
            checkbox = checkbox.replace("$_$", str(row))
            get_username = self.s.get_text(find_user)

            if get_username == username:
                self._delete_element(checkbox, self.info['loc_cfg_user_delete_button'], "user")
                logging.info("Delete user " + username + " successfully")
                #clean search context
                self._fill_search_txt(self.info['loc_cfg_user_search_textbox'], '')
                return

            if row == max_user_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_user_next_image'])

            row = row + 1
            time.sleep(1)

        logging.info("User " + username + " not existed in the User table")
        #clean search context
        self._fill_search_txt(self.info['loc_cfg_user_search_textbox'], '')

    def _delete_all_user(self):
        """
        Remove all users out of local database

        Input: none
        Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_USERS, 3)
        max_users_row = int(self.info['const_cfg_max_row_user'])

        delete_entries = 0
        total_users = 1
        while delete_entries < 150 and total_users > 0:
            if not self.s.is_checked(self.info['loc_cfg_user_check_all_checkbox']):
                time.sleep(2)
                self.s.click_and_wait(self.info['loc_cfg_user_check_all_checkbox'], 4)

            self.s.choose_ok_on_next_confirmation()
            self.s.click_and_wait(self.info['loc_cfg_user_delete_button'], 4)
            if self.s.is_confirmation_present(5):
                self.s.get_confirmation()

            delete_entries += max_users_row
            time.sleep(4)
            total_users = int(self._get_total_number(self.info['loc_cfg_user_total_number_span'], "Users"))
            time.sleep(4)

        return total_users


    def _upgrade_zd(self, img_path, default = False):
        #Jacky Luh updated by 2012-06-02
        self.navigate_to(self.ADMIN, self.ADMIN_UPGRADE)

        upgrade_file_textbox = self.info['loc_admin_browse_file_button']
        if not self.s.is_element_present(upgrade_file_textbox):
            raise Exception("Element %s not found" % upgrade_file_textbox)

        if self.browser_type == "ie":
            dlg = StandardDialog(StandardDialog.IE_CHOOSE_FILE_DLG, img_path)
            manager = DialogManager()
            manager.add_dialog(dlg)
            manager.start()
            self.s.click_and_wait(upgrade_file_textbox)
            manager.join(10)
            manager.shutdown()

        else:
            try:
                self.s.type(upgrade_file_textbox, img_path)
            except:
                raise Exception("Can not set value %s to the locator %s" % (img_path, upgrade_file_textbox))

        logging.info("Wait for build to be fully uploaded. This process takes some seconds. Please wait...")
        # Bypass the confirmation to backup the config file which happens on ZD7.1
        self.s.choose_cancel_on_next_confirmation()
        perform_upgrade_button = self.info['loc_admin_perform_upgrd_button']#    'loc_admin_perform_upgrd_button':r"//input[@id='perform-upgrade']",
        error_upgrade_span = self.info['loc_admin_error_upgrade_span'] #    'loc_admin_error_upgrade_span':r"//span[@id='error-upgrade']"
        restore_default = self.info['loc_admin_error_restore_default_radio']#    'loc_admin_error_restore_default_radio':r"//input[@id='upgrade_errorinput_1']",
        restore_previous = self.info['loc_admin_error_restore_previous_radio']#    'loc_admin_error_restore_previous_radio':r"//input[@id='upgrade_errorinput_0']",
        continue_upgrade = self.info['loc_admin_continue_upgrade']#    'loc_admin_continue_upgrade':r"//a[@id='continue-upgrade']",
        #Chico@2014-8-25, fix bug of ZF-9797
        uploading = self.info['loc_admin_uploading']#    'loc_admin_uploading':r"span[@id='//uploaded-upgrade']",
        t0 = time.time()
        #Jacky.Luh updated by 2012-07-06, ZD1100, upload the image, more than 1 min.
        time_out = 120
        #Chico: uploading firmware and wait till upgrade/continue button raise
        while True:
            if self.s.is_element_present(uploading, 1):
                if 'Uploading' in self.s.get_text(uploading, 1):
                    logging.info('Fireware uploading, please wait......')
                elif self.s.is_element_present(perform_upgrade_button) and self.s.is_visible(perform_upgrade_button):
                    break
                elif self.s.is_element_present(continue_upgrade):
                    break
                else:
                    pass
            else:
                logging.info('Unable to know the status because %s not found' %uploading)
                
            if time.time() - t0 > time_out:
                raise Exception("The upgrade process was not completed after %s seconds" % time_out)
            
            time.sleep(2)

        #Chico: based on different error message and options, check correct option
        if self.s.is_element_present(error_upgrade_span) and self.s.is_visible(error_upgrade_span):
            msg = self.s.get_text(error_upgrade_span)
            logging.info('Got an error message: %s' %msg)
            if "The Support Entitlement file is invalid" in msg:
                self.s.click_and_wait(continue_upgrade)
                #Chico, 2014-11-21, after 'entitlement', if has not-support-any-more APs, the following codes are need
                if self.s.is_element_present(error_upgrade_span) and self.s.is_visible(error_upgrade_span):
                    msg = self.s.get_text(error_upgrade_span)
                    logging.info('Got the second level error message: %s' %msg)
                    if "does not support the following APs" in msg:
                        self.s.click_and_wait(restore_default)  
                #Chico, 2014-11-21, after 'entitlement', if has not-support-any-more APs, the following codes are need
            elif "does not support the following APs" in msg:
                self.s.click_and_wait(restore_default)
            elif "downgrade package is applicable to" not in msg and "upgrade package is applicable to" not in msg:
                raise Exception(msg)
            else:    
                if default and self.s.is_element_present(restore_default):
                    self.s.click_and_wait(restore_default)
                elif self.s.is_element_present(restore_previous):
                    self.s.click_and_wait(restore_previous)
        else:
            if default and self.s.is_element_present(restore_default):
                self.s.click_and_wait(restore_default)
            elif self.s.is_element_present(restore_previous):
                self.s.click_and_wait(restore_previous)
        #Chico@2014-8-25, fix bug of ZF-9797
                    
        # Ensure that the confirmation is removed if it does exist
        if self.s.is_confirmation_present(5):
            logging.info("2.after upload file,Got confirmation: %s" % self.s.get_confirmation())
        
        #Chico@2014-6-6, ZoneFlex 2942/2741/2741-ext removed from 9.8 supporting.ZF-8623
#        if self.s.is_element_present(error_upgrade_span) and self.s.is_visible(error_upgrade_span):
#            _info = self.s.get_text(error_upgrade_span)
#            logging.info("Got a upgrade speical warning information: %s" % _info)
#            if "2942/2741/2741-ext" in _info:
#                self.s.click_and_wait(restore_default)
#            else:    
#                if default and self.s.is_element_present(restore_default):
#                    self.s.click_and_wait(restore_default)
#                elif self.s.is_element_present(restore_previous):
#                    self.s.click_and_wait(restore_previous)
#        else:
#            if default and self.s.is_element_present(restore_default):
#                self.s.click_and_wait(restore_default)
#            elif self.s.is_element_present(restore_previous):
#                self.s.click_and_wait(restore_previous)
        #Chico@2014-6-6, ZoneFlex 2942/2741/2741-ext removed from 9.8 supporting.ZF-8623
                #Chico@2014-8-25, fix bug of ZF-9797

        # Bypass the confirmation to perform upgrading
        self.s.choose_ok_on_next_confirmation()
#        self.s.choose_ok_on_next_confirmation()
        self.s.click_and_wait(perform_upgrade_button)
        logging.info('click perform_upgrade_button')
        if self.s.is_confirmation_present(5):
            cfm=self.s.get_confirmation()
            logging.info('confimation got %s'%cfm)

        logging.info("The Zone Director is being upgraded. This process takes from 3 to 5 minutes. Please wait...")

    #Jacky Luh updated by 2012-06-02
    def _check_upgrade_sucess(self, login_ip_addr = None, default = False, news_conf = {}):
#        default_conf = {'system_name': 'Ruckus',
#                        'guest_wlan_name': 'Ruckus-Guest',
#                        'language': 'English',
#                        'admin_name': 'admin',
#                        'create_user_account_is_checked': False,
#                        'guest_wlan_enabled': False,
#                        'wireless1_name': 'Ruckus-Wireless-1',
#                        'mesh_enabled': False,
#                        'country_code': 'United States',
#                        'dhcp': True,
#                        'authentication_open': False,
#                        'wireless1_enabled': True,
#                        'admin_password': ''}
        default_conf = {}
        new_conf = {'ip_dualmode': False, 
                    'mesh_enabled': False}
        new_conf.update(news_conf)
        factory_id = False
        if login_ip_addr:
            self.ip_addr = login_ip_addr
            self.url = "https://" + str(self.ip_addr) + '/admin/login.jsp'

        time_out = 1200
        start_time = time.time()
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(self.ip_addr)
            if res.find("Timeout") != -1:
                break

            time.sleep(2)

        logging.info("The Zone Director is being restarted. Please wait...")

        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout")

            res = ping(self.ip_addr)
            if res.find("Timeout") == -1:
                break

            time.sleep(2)
        logging.info("The Zone Director has been upgraded successfully.")
        time.sleep(15)
        logging.info("Please wait while I am trying to navigate to the ZD's main URL[%s]." % self.url)
        time_out = 600
        start_time = time.time()
        while True:
            if time.time() - start_time > time_out:
                raise Exception("Error: Timeout. Cannot url to ZD[%s]." % self.url)
            try:
                self.refresh()
                #self.s.open(self.url)#Chico, 2014-11-19, sometimes selenium can't find the following language factor
                if default or self.s.is_element_present(self.info['loc_wzd_language_option']):
                    if self.mesh_enabled:
                        new_conf['mesh_enabled'] = True           
                    factory_id = True    
                    self._setup_wizard_cfg_totally_followig_defalut_cfg(default_conf, new_conf)
                    self.logout()
                else:
                    self.login()
                    self.logout()
                break

            except:
                time.sleep(2)
                pass

        # Make sure that selenium can navigate to Zone Director after upgrading
        #Chico, 2014-11-19, sometimes selenium can't find the logging button
        start_time = time.time()
        while True:
            if not self.s.is_element_present(self.info['loc_login_ok_button']):
                logging.info("Failed to navigate to the ZD's web UI, wait another 5 seconds then try again.")
                if time.time() - start_time > time_out:
                    raise Exception("Error: could not navigate to the original url")
                else:
                    time.sleep(5)
            else:
                logging.info("Succeed to navigate to the ZD's web UI.")
                break
        #Chico, 2014-11-19, sometimes selenium can't find the logging button

        return factory_id


    def _upgrade(self, img_path, factory = False, build_version = None):
        """ Upgrade the Zone Director to the image specified by the img_path path.

        Make sure that all connected APs are upgraded and connected successfully after upgrading.
        After upgrading, this method will navigate to the ZD's URL without logging in
        """
        #Jacky Luh updated by 2012-06-26
        self._upgrade_zd(img_path, factory)
        factory_id = self._check_upgrade_sucess()
                
        return factory_id


    def get_version(self):
        return self._get_version()['release']


    def _get_version(self):
        """
        Get current version of ZD
        """
        self.navigate_to(self.ADMIN, self.ADMIN_UPGRADE, 2)
        cur_ver = self.s.get_text(self.info['loc_admin_current_version_span'])
        cur_ver = cur_ver.split()

        self.version = {
            'release': cur_ver[0],
            'build': cur_ver[2],
            'version': '.'.join([cur_ver[0], cur_ver[2]]),
        }

        return self.version


    def _get_all_ap_info(self):
        """
        WARNING: OBSOLETE, use get_all_ap_briefs in lib.zd.aps instead

        Get all information of all APs appearing in the AP-Summary table
        Input: none
        Output:
        - If AP-Summary table is not empty, return a list of dictionary,
        in there, each dictionary contains all information of each AP
        - If AP-Summary table is empty, return an empty list
        """
        return WGT.map_rows(
            APS._get_all_ap_briefs(self),
            AP_INFO_HDR_MAP
        )


    def _get_ap_info(self, mac_addr):
        """
        WARNING: OBSOLETE, use get_ap_brief_by_mac_addr in lib.zd.aps instead

        Get all information of particular AP based on its mac address, including description, model, status...
        Input:
        - mac_addr: mac address of such an AP. It is used to find that AP in the AP-Summary table
        Output:
        - If the AP is found, return a dictionary with full information of that AP
        - If AP is not found, return an empty dictionary.
        """
        return WGT.map_row(
            APS._get_ap_brief_by(self, dict(mac = mac_addr)),
            AP_INFO_HDR_MAP
        )


    def _get_ap_attrib_at_col(self, xpath, traverse_row):
        if not self.info.has_key(xpath) or not self.info[xpath]:
            return ''

        return self.s.get_text(self.info[xpath].replace("$_$", str(traverse_row)))


    def get_ap_info_ex(self, mac_addr):
        """
        WARNING: OBSOLETE, use get_ap_detail_by_mac_addr in lib.zd.aps instead

        In addition, DO NOT call this method when not necessary. There are other access methods
        to get each table-specific detail of an AP by MAC Addr:
        - get_ap_detail_general_by_mac_addr: General
        - get_ap_detail_info_by_mac_addr: Info
        - get_ap_detail_radio_by_mac_addr: Radio 802.11b/g or Radio 802.11g/n
        - get_ap_detail_wlans_by_mac_addr: WLANs
        - get_ap_detail_neighbor_by_mac_addr: Neighbor APs

        Get more information of the AP with given mac_addr
        Input:
        @param mac_addr: MAC address of the AP
        @return: a dictionary of subdictionaries:
            general = get_ap_detail_general_by_mac_addr,
            info = get_ap_detail_info_by_mac_addr,
            radio = get_ap_detail_radio_by_mac_addr,
            wlans = get_ap_detail_wlans_by_mac_addr,
            neighbor = get_ap_detail_neighbor_by_mac_addr,
            uplink = get_ap_detail_uplink_ap,
            downlink = get_ap_detail_downlink_aps,

        Refer to lib.zd.aps for dict keys.
        """

        return APS.get_ap_detail_by_mac_addr(self, mac_addr)


    def _delete_all_aps(self):
        """
        Remove all APs out of the Access Points table
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_POINT)
        show_more_button=self.info['loc_cfg_ap_show_more_button']
        
        ap_total = self.get_total_aps_num_from_configure_tab()
        logging.info("There are total %s APs before delete" % ap_total)
        if ap_total != "0":
            while self.s.is_visible(show_more_button):
                self.s.click_and_wait(show_more_button)
            self._delete_element(self.info['loc_cfg_ap_select_all_checkbox'], self.info['loc_cfg_ap_delete_button'], "APs")
            time.sleep(1)
            ap_total = self.get_total_aps_num_from_configure_tab()
            logging.info("There are total %s APs after delete" % ap_total)
        else:
            return

    def _delete_ap(self, mac_addr):
        """
        Remove an AP out of the Access Point table
        Input:
        - mac_addr: mac address of the deleted AP
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_POINT)

        ap_total = self.get_total_aps_num_from_configure_tab()
        max_ap_per_page = int(self.info['const_cfg_ap_table_size'])
        row = 1

        for i in range(int(ap_total)):
            ap_row = self.info['loc_cfg_ap_mac_cell']
            ap_row = ap_row.replace("$_$", str(row))
            checkbox = self.info['loc_cfg_ap_select_checkbox']
            checkbox = checkbox.replace("$_$", str(row))
            mac = self.s.get_text(ap_row)
            # JLIN@20081111 get mac_addr from tbconfig is the upper case, but mac from screen is lowercase
            mac_addr = mac_addr.lower()

            if mac.lower() == mac_addr:
                self._delete_element(checkbox, self.info['loc_cfg_ap_delete_button'], "AP")
                return

            if row == max_ap_per_page:
                self.s.click_and_wait(self.info['loc_cfg_ap_next_image'])
                row = 0

            row = row + 1

        raise Exception("Can not find the AP with mac address %s in the AccessPoints table" % mac_addr)

    #Updated by cwang@20130529, remove v2.
    def set_ap_cfg(self, ap_cfg):
        '''
        WARNING: ADAPTER, please use lib.zd.ap.set_ap_config_by_mac func for new development.
        If there is no need to set all AP configuration, use individual func:
        . lib.zd.ap.set_ap_general_by_mac_addr
        . lib.zd.ap.set_ap_radio_by_mac_addr
        . lib.zd.ap.set_ap_ip_config_by_mac_addr
        . lib.zd.ap.set_ap_mesh_by_mac_addr
        '''
        mac_addr = ap_cfg['mac_addr']
        radio_list = AP._get_ap_supported_radios(self, mac_addr)

        AP._nav_to(self)
        AP._open_ap_dialog_by_mac(self, ap_cfg['mac_addr'])

        # Mapping Radio Config
        for radio in radio_list:
            if radio not in ['bg', 'ng']:
                pass

            radio_param = {
                'channel': ap_cfg['channel'] if ap_cfg.has_key('channel') else None,
                'channelization': ap_cfg['channelization'] if ap_cfg.has_key('channelization') else None,
                'power': ap_cfg['txpower'] if ap_cfg.has_key('txpower') else None,
            }
            AP._set_ap_radio(self, radio, radio_param)

        # Mapping Mesh Config
        mesh_mode = 'auto'
        if ap_cfg.has_key('mesh_uplink_aps') and ap_cfg['mesh_uplink_aps']:
            mesh_param = {
                'uplink_mode': 'manual', #[smart, manual] are valid uplink modes
                'uplink_aps': ap_cfg['mesh_uplink_aps'], #mac_addr lists
            }
        else:
            mesh_param = {
                'uplink_mode': 'smart', #[smart, manual] are valid uplink modes
            }

        AP._set_ap_mesh(self, mesh_mode, mesh_param)


        # Mapping IP Config
        if ap_cfg.has_key('ip_management') and ap_cfg['ip_management']:
            ip_mode = {
                'keep_ap_setting': 'as_is',
                'dhcp': 'dhcp',
                'manual': 'manual',
            }[ap_cfg['ip_management']['by-dhcp']]
            ip_param = ap_cfg['ip_management']
            # will not call the pop() if there is no the key in the dictionary
            # @an.nguyen@ruckuswireless.com by Nov 2011
            if ip_param.has_key('by-dhcp'): ip_param.pop('by-dhcp')
            if ip_param.has_key('ip_mode'): ip_param.pop('ip_mode')

            AP._set_ap_ip_config(self, ip_mode, ip_param)


        # Save and close the dialog
        AP._save_and_close_ap_dialog(self)
        self.re_navigate()

    #Updated by cwang@20130529, remove v2 tag
    def get_ap_cfg(self, mac_addr):
        '''
        WARNING: ADAPTER, please use lib.zd.ap.get_ap_config_by_mac func for new development.
        If not all AP configuration is needed, use individual func:
        . lib.zd.ap.get_ap_general_info_by_mac
        . lib.zd.ap.get_ap_radio_config_by_mac
        . lib.zd.ap.get_ap_ip_config_by_mac
        . lib.zd.ap.get_ap_mesh_config_by_mac
        '''
        ap_config = AP.get_ap_config_by_mac(self, mac_addr)
        ap_config_info = {}

        ap_config_info['mac_addr'] = mac_addr

        # Mapping Radio Config
        radio_config = ap_config['radio_config']
        for radio in radio_config.iterkeys():
            if radio not in ['bg']:
                ap_config_info['channelization'] = radio_config[radio]['channelization']

            ap_config_info['channel'] = radio_config[radio]['channel']
            ap_config_info['txpower'] = radio_config[radio]['power']
            ap_config_info['wlangroup'] = radio_config[radio]['wlangroups']


        # Mapping IP Config
        ap_config_info['ip_management'] = {}
        ip_config = ap_config['ip_config']
        ap_config_info['ip_management']['by-dhcp'] = {
            'as_is': 'keep_ap_setting',
            'manual': 'manual',
            'dhcp': 'dhcp',
        }[ip_config['ip_mode']]

        if ip_config['ip_mode'] == 'manual':
            ap_config_info['ip_management'].update(ip_config['ip_param'])


        # Mapping Mesh COnfig
        mesh_config = ap_config['mesh_config']
        ap_config_info['mesh_mode'] = mesh_config['mesh_mode']

        ap_config_info['mesh_uplink_aps'] = []
        if mesh_config['mesh_mode'] in ['auto', 'mesh']:
            ap_config_info['mesh_uplink_mode'] = mesh_config['mesh_param']['uplink_mode'].capitalize()
            ap_config_info['mesh_uplink_aps'] = mesh_config['mesh_param']['uplink_aps']


        # Done mapping
        return ap_config_info


    def _get_client_attrib_at_col(self, xpath, row):
        return self._get_ap_attrib_at_col(xpath, row)


    def get_active_client_list(self):
        """
        get_active_client_list get information of all client associate to AP in page Monitor->Active Client and
        returns a list of dictionaries each of which contains information of one client:
        [{'mac':'', 'ip_addr':''}]
        """
        return WGT.map_rows(
            CAC._get_all_clients_briefs(self),
            ACTIVE_CLIENT_HDR_MAP,
        )


    def remove_all_active_clients(self):
        self.navigate_to(self.MONITOR, self.MONITOR_CURRENTLY_ACTIVE_CLIENTS, 2)

        total_clients = self._get_total_number(self.info['loc_mon_clients_total_number_span'], "Current Active Clients")
        delete_first_client_span = self.info['loc_mon_clients_delete_span'].replace("$_$", "0")
        for i in range(int(total_clients)):
            self.s.click_and_wait(delete_first_client_span)

        logging.info("Delete all active clients successfully")


    def __del__(self):
        """ This method is a destructor.

        It will be called when an instance of this class has been killed.
        All browsers will be closed and the selenium server will be killed
        """
        self.destroy()

    def _get_system_name(self):
        """
        This method is used for getting the System Name.

        - Input: none
        - Output: System Name
        """
        #stan@20110120
        self.navigate_to(self.DASHBOARD, self.NOMENU, loading_time = 5)

        logging.info("Get the system name")

        return self.s.get_text(self.info['loc_dashboard_sysinfo_name_cell'])


    def _get_ip_cfg_status(self):
        """
        This method is used for getting the ip configuration status. The status may be 'static' or 'dhcp'

        - Input: none
        - Output: the current status of ip configuration ("static" or "dhcp")
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)
        if self.s.is_checked(self.info['loc_cfg_system_ip_manual_radio']):
            return "static"

        else:
            return "dhcp"


    def _set_ip_cfg_status(self, status):
        """
        This method is used for setting the ip configuration of the Zone Director to whether 'static' or 'dhcp'

        - Input: a status ('static' or 'dhcp')
        - Output: none
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)
        if status == "static":
            if self._get_ip_cfg_status() != "static":
                self.s.click_and_wait(self.info['loc_cfg_system_ip_manual_radio'])

        else:
            if self._get_ip_cfg_status() != "dhcp":
                self.s.click_and_wait(self.info['loc_cfg_system_ip_dhcp_radio'])

        self.s.click_and_wait(self.info['loc_cfg_system_mgt_ip_apply_button'], 5)

        logging.info("The IP configuration status has been set to '%s'" % status)


    def _get_serial_number(self):
        """
        This method is used for getting the System Name from the Dashboard page

        - Input: none
        - Output: System Name
        """
        self.navigate_to(self.DASHBOARD, self.NOMENU, loading_time = 2)

        return self.s.get_text(self.info['loc_dashboard_sysinfo_serial_cell'])


    def _reset_factory(self, wait_for_alive = True):
        """ Set the Zone Director to factory configuration. This method makes sure that the Zone Director has been restarted successfully
        by using the 'ping' function.

        - Input: none
        - Output: none

        """
        self.navigate_to(self.ADMIN, self.ADMIN_BACKUP)
        self.s.choose_ok_on_next_confirmation()
        self.s.click_and_wait(self.info['loc_admin_reset_factory_button'], 0.5)
        if not self.s.is_confirmation_present(5):
            raise Exception ("Error: No confirmation dialog appears")

        self.s.get_confirmation()
        if wait_for_alive:
            self._reset_factory_wait_for_alive_s1()


    # spilt to here to support ZD mgmtVlan
    def _reset_factory_wait_for_alive_s1(self):
        logging.info("The Zone Director is being reset. Please wait...")
        # Keeping pinging to the Zone Director until it has been restarted successfully
        time_out = 420
        start_time = time.time()
        while True:
            if (time.time() - start_time) > time_out:
                raise Exception("Error: Timeout")

            res = ping(self.ip_addr)
            if res.find("Timeout") != -1:
                break

            time.sleep(2)

        self._reset_factory_wait_for_alive_s2(time_out, start_time)


    def _reset_factory_wait_for_alive_s2(self, time_out = 360, start_time = 0):
        if not start_time:
            start_time = time.time()
        logging.info("The Zone Director is being restarted. Please wait...")
        bugme.do_trace('TRACE_RAT_ON_RESET_ZD')
        while True:
            if (time.time() - start_time) > time_out:
                raise Exception("Error: Timeout")

            res = ping(self.ip_addr)
            if res.find("Timeout") == -1:
                break

        # TAK@20081110 For 7.1 the value > 10; 6.0 we saw it too;
        time.sleep(20)
        logging.info("The Zone Director has been reset successfully to factory configuration.")



    def _verify_config_item(self, default_conf, item):
        '''
         .verifies provided config against default setup wizard config.
         .this is for internal use only.
        '''
        if item['value'] != default_conf[item['name']]:
            if type(default_conf[item['name']]) is str and  item['value'].lower() == default_conf[item['name']].lower():
                logging.info("The %s was '%s' instead of '%s', but it is accepted." % (item['description'], item['value'], default_conf[item['name']]))
            else:
                error_msg = "The %s was '%s' instead of '%s'" % \
                            (item['description'], item['value'], default_conf[item['name']])

                raise Exception(error_msg)


    def _config_wizard_items(self, items, default_conf = {}, new_conf = {}):
        '''
        '''
        for (item, cfg) in items.iteritems():
            # Verify the current item conf against the default value
            if default_conf.has_key(item):
                if cfg.has_key('get_func') and cfg['get_func']:
                    cfg.update({
                        'value': cfg['get_func'](cfg['locator']),
                        'name': item,
                    })
                    self._verify_config_item(default_conf, cfg)

            # Change to new value if required
            if new_conf.has_key(item):
                if cfg.has_key('set_func') and cfg['set_func']:
                    cfg['set_func'](cfg['locator'], new_conf[item])


    def _config_wizard_language(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Language:
        new_conf = {
            'language': 'English',
        }
        '''
        items = {
            'language': {
                'description': 'Language',
                'get_func': self.s.get_selected_label,
                'locator': self.info['loc_wzd_language_option'],
                'set_func': self.s.select_option,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)


    def _config_wizard_system_name(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for System Name:
        new_conf = {
            'system_name': 'ruckus',
        }
        '''
        items = {
            'system_name': {
                'description': 'System Name',
                'get_func': self.s.get_value,
                'locator': self.info['loc_wzd_system_name_textbox'],
                'set_func': self.s.type_text,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)


    def _config_wizard_country_code(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Country Code:
        new_conf = {
            'country_code': 'United States',
        }
        '''
        items = {
            'country_code': {
                'description': 'Country Code',
                'get_func': self.s.get_selected_label,
                'locator': self.info['loc_wzd_country_code_option'],
                'set_func': self.s.select_option,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)


    def _config_wizard_mesh_enabled(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Mesh Enabled:
        new_conf = {
            'mesh_enabled': True,
            'mesh_name': 'Mesh-100903000729',
            'mesh_passphrase': 'btHHeJHfVNa5QuwOPR9A00sHYjSMHAok28AdQVurZ4PpdVkeUJHJDDIksxhxZPV',
        }
        '''
        items = {
            'mesh_enabled': {
                'description': 'Mesh Enabled status',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_mesh_checkbox'],
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('mesh_enabled'):
            if new_conf['mesh_enabled']:
                self.s.click_if_not_checked(items['mesh_enabled']['locator'])

        if self.s.is_checked(items['mesh_enabled']['locator']):
            self._config_wizard_mesh_details(default_conf, new_conf)


    def _config_wizard_mesh_details(self, default_conf, new_conf):
        '''
        If new_conf is provided, it should be:
        .new config for Mesh Enabled:
        new_conf = {
            'mesh_enabled': True,
            'mesh_name': 'Mesh-100903000729',
            'mesh_passphrase': 'btHHeJHfVNa5QuwOPR9A00sHYjSMHAok28AdQVurZ4PpdVkeUJHJDDIksxhxZPV',
        }
        '''
        items = {
            'mesh_name': {
                'description': 'Mesh Enabled name',
                'get_func': self.s.get_value,
                'locator': self.info['loc_wzd_mesh_name_textbox'],
                'set_func': self.s.type_text,
            },
            'mesh_passphrase': {
                'locator': self.info['loc_wzd_mesh_passphrase_textbox'],
                'set_func': self.s.type_text,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)


    def _mesh_func_check(self, new_conf):
        '''
        '''
        mesh_enabled = self.s.is_checked(self.info['loc_wzd_mesh_checkbox'])
        if bool(new_conf['mesh_enabled']) != bool(mesh_enabled):
            return True

        return False


    def _config_wizard_management_ip(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Management IP mode:
        new_conf = {
            'ip_dualmode': True, #only one key is set to True
            'ip_v4mode': False,
            'ip_v6mode': False,
        }
        '''
        items = {
            'ip_dualmode': {
                'description': 'IPv4 and IPv6',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_ip_dualmode_radio'] if \
                            self.info.has_key('loc_wzd_ip_dualmode_radio') else "",
                'set_func': self.s.click_if_not_checked,
            },
            'ip_v4mode': {
                'description': 'IPv4',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_ip_v4mode_radio'] if \
                            self.info.has_key('loc_wzd_ip_v4mode_radio') else "",
                'set_func': self.s.click_if_not_checked,
            },
            'ip_v6mode': {
                'description': 'IPv6',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_ip_v6mode_radio'] if \
                            self.info.has_key('loc_wzd_ip_v6mode_radio') else "",
                'set_func': self.s.click_if_not_checked,
            },
        }
        self._config_wizard_items(items, default_conf, new_conf)

        if not items['ip_dualmode']['locator'] or \
        self.s.is_checked(items['ip_dualmode']['locator']) or \
        self.s.is_checked(items['ip_v4mode']['locator']):
            self._config_wizard_ipv4_dhcp_enabled(default_conf, new_conf)

        if items['ip_dualmode']['locator'] and ( \
        self.s.is_checked(items['ip_dualmode']['locator']) or \
        self.s.is_checked(items['ip_v6mode']['locator'])):
            self._config_wizard_ipv6_autoconfig(default_conf, new_conf)


    def _config_wizard_ipv4_dhcp_enabled(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Management IPv4 manual mode:
        new_conf = {
            'dhcp_enabled': True,
        }
        '''
        items = {
            'dhcp_enabled': {
                'description': 'Management IPv4 mode',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_ip_dhcp_radio'],
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('dhcp_enabled'):
            if new_conf['dhcp_enabled']:
                self.s.click_and_wait(items['dhcp_enabled']['locator'])

            else:
                self.s.click_and_wait(self.info['loc_wzd_ip_manual_radio'])

        if self.s.is_checked(self.info['loc_wzd_ip_manual_radio']):
            self._config_wizard_ipv4_manual(default_conf, new_conf)


    def _config_wizard_ipv4_manual(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Management IPv4 manual mode:
        new_conf = {
            'dhcp_enabled': False,
            'ip_manual': True, #this key will not be used
            'ip_addr': '192.168.0.2',
            'net_mask': '255.255.255.0',
            'gateway': '192.168.0.253',
            'dns1': '192.168.0.252',
            'dns2': '',
        }
        '''
        items = {
            'ip_manual': {
                'description': 'Management IPv4 mode',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_ip_manual_radio'],
            },
            'ip_addr': {
                'locator': self.info['loc_wzd_ip_addr_textbox'],
                'set_func': self.s.type_text,
            },
            'net_mask': {
                'locator': self.info['loc_wzd_ip_net_mask_textbox'],
                'set_func': self.s.type_text,
            },
            'gateway': {
                'locator': self.info['loc_wzd_ip_gateway_textbox'],
                'set_func': self.s.type_text,
            },
            'dns1': {
                'locator': self.info['loc_wzd_ip_dns1_textbox'],
                'set_func': self.s.type_text,
            },
            'dns2': {
                'locator': self.info['loc_wzd_ip_dns2_textbox'],
                'set_func': self.s.type_text,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)


    def _config_wizard_ipv6_autoconfig(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Management IPv6 autoconfig mode:
        new_conf = {
            'ipv6_autoconfig': True,
        }
        '''
        items = {
            'ipv6_autoconfig': {
                'description': 'Management IPv6 mode',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_ip_ipv6_autoconfig_radio'],
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('ipv6_autoconfig'):
            if new_conf['ipv6_autoconfig']:
                self.s.click_and_wait(items['ipv6_autoconfig']['locator'])

            else:
                self.s.click_and_wait(self.info['loc_wzd_ip_ipv6_manual_radio'])

        if self.s.is_checked(self.info['loc_wzd_ip_ipv6_manual_radio']):
            self._config_wizard_ipv4_manual(default_conf, new_conf)


    def _config_wizard_ipv6_manual(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Management IPv6 manual mode:
        new_conf = {
            'ipv6_autoconfig': False,
            'ipv6_manual': True, #this key will not be used
            'ipv6_addr': 'fe80::224:82ff:fe32:d3b1',
            'ipv6_prefix': '64',
            'ipv6_gateway': '2010::1',
            'ipv6_dns1': '',
            'ipv6_dns2': '',
        }
        '''
        items = {
            'ipv6_manual': {
                'description': 'Management IPv6 mode',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_ip_ipv6_manual_radio'],
            },
            'ipv6_addr': {
                'locator': self.info['loc_wzd_ip_ipv6_addr_textbox'],
                'set_func': self.s.type_text,
            },
            'ipv6_prefix': {
                'locator': self.info['loc_wzd_ip_ipv6_prefix_textbox'],
                'set_func': self.s.type_text,
            },
            'ipv6_gateway': {
                'locator': self.info['loc_wzd_ip_ipv6_gateway_textbox'],
                'set_func': self.s.type_text,
            },
            'ipv6_dns1': {
                'locator': self.info['loc_wzd_ip_ipv6_dns1_textbox'],
                'set_func': self.s.type_text,
            },
            'ipv6_dns2': {
                'locator': self.info['loc_wzd_ip_ipv6_dns2_textbox'],
                'set_func': self.s.type_text,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)


    def _config_wizard_wireless1_enabled(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for default Wireless LAN 1:
        new_conf = {
            'wireless1_enabled': True,
            'wireless1_name': 'ruckus-Guest',
            'authentication_open': True,
        }
        '''
        items = {
            'wireless1_enabled': {
                'description': 'default WLAN "Wireless 1"',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_1st_wlan_checkbox'],
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('wireless1_enabled'):
            if new_conf['wireless1_enabled']:
                self.s.click_if_not_checked(items['wireless1_enabled']['locator'])

            else:
                self.s.click_if_checked(items['wireless1_enabled']['locator'])

        if self.s.is_checked(items['wireless1_enabled']['locator']):
            self._config_wizard_wireless1_details(default_conf, new_conf)


    def _config_wizard_wireless1_details(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Wireless LAN 1:
        new_conf = {
            'wireless1_enabled': True,
            'wireless1_name': 'ruckus-Guest',
            'authentication_open': True,
        }
        '''
        items = {
            'wireless1_name': {
                'description': 'Wireless LAN 1 name',
                'get_func': self.s.get_value,
                'locator': self.info['loc_wzd_1st_wlan_name'],
                'set_func': self.s.type_text,
            },
            'authentication_open': {
                'description': 'Wireless LAN 1 authentication method',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_1st_wlan_open_auth_radio'],
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('authentication_open'):
            if new_conf['authentication_open']:
                self.s.click_if_not_checked(items['authentication_open']['locator'])

            else:
                self.s.click_if_checked(items['authentication_open']['locator'])


    def _config_wizard_guest_wlan_enabled(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Guest WLAN:
        new_conf = {
            'guest_wlan_enabled': True,
            'guest_wlan_name': 'ruckus-Guest',
        }
        '''
        items = {
            'guest_wlan_enabled': {
                'description': 'Guest WLAN"',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_guest_wlan_checkbox'],
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('guest_wlan_enabled'):
            if new_conf['guest_wlan_enabled']:
                self.s.click_if_not_checked(items['guest_wlan_enabled']['locator'])

        if self.s.is_checked(items['guest_wlan_enabled']['locator']):
            self._config_wizard_guest_wlan_details(default_conf, new_conf)


    def _config_wizard_guest_wlan_details(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for Guest WLAN:
        new_conf = {
            'guest_wlan_enabled': True,
            'guest_wlan_name': 'ruckus-Guest',
        }
        '''
        items = {
            'guest_wlan_name': {
                'description': 'Guest WLAN name',
                'get_func': self.s.get_value,
                'locator': self.info['loc_wzd_guest_wlan_name_textbox'],
                'set_func': self.s.type_text,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)


    def _config_wizard_admin_user(self, default_conf = {}, new_conf = {}):
        '''
        If new_conf is provided, it should be:
        .new config for admin:
        new_conf = {
            'admin_name': 'admin',
            'admin_password': '',
        }

        .new config for user
        new_conf = {
            'create_user_account_is_checked': True,
            'new_user_name': '',
            'new_user_password': '',
        }
        '''
        items = {
            'admin_name': {
                'description': 'admin name"',
                'get_func': self.s.get_value,
                'locator': self.info['loc_wzd_admin_name_textbox'],
                'set_func': self.s.type_text,
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('admin_password'):
            self.s.type_text(
                self.info['loc_wzd_admin_password1_textbox'],
                new_conf['admin_password']
            )
            self.s.type_text(
                self.info['loc_wzd_admin_password2_textbox'],
                new_conf['admin_password']
            )

        else:
            self.s.type_text(
                self.info['loc_wzd_admin_password1_textbox'],
                self.password
            )
            self.s.type_text(
                self.info['loc_wzd_admin_password2_textbox'],
                self.password
            )

        # create new account
        items = {
            'create_user_account_is_checked': {
                'description': 'create new account status"',
                'get_func': self.s.is_checked,
                'locator': self.info['loc_wzd_create_user_checkbox'],
            },
        }

        self._config_wizard_items(items, default_conf, new_conf)

        if new_conf.has_key('create_user_account_is_checked'):
            if new_conf['create_user_account_is_checked']:
                self.s.click_if_not_checked(
                    items['create_user_account_is_checked']['locator']
                )

        if self.s.is_checked(items['create_user_account_is_checked']['locator']):
            if new_conf.has_key('new_user_name'):
                self.s.type_text(
                    self.info['loc_wzd_user_name_textbox'],
                    new_conf['new_user_name']
                )

            if new_conf.has_key('new_user_password'):
                self.s.type_text(
                    self.info['loc_wzd_user_password1_textbox'],
                    new_conf['new_user_password']
                )
                self.s.type_text(
                    self.info['loc_wzd_user_password2_textbox'],
                    new_conf['new_user_password']
                )



    def _setup_wizard_cfg(self, default_conf = {}, new_conf = {}):
        """
        If we don't pass any parameter, this method is used for setting up
        the wizard with default information.
        If we pass a dictionary of default values as below, it will compare
        these values with the values on the setup wizard. If there is any pair
        that is not matched, it will raise an Exception telling us the reason of
        this failure.

        @param default_conf = {
            'language': 'English',
            'system_name': 'ruckus',
            'country_code': 'United States',
            'mesh_enabled': False,
            'ip_dualmode': True,
            'dhcp_enabled': False, #True on Udaipur
            'ipv6_autoconfig': True,
            'wireless1_enabled': True,
            'wireless1_name': 'Ruckus-Wireless-1',
            'authentication_open': True,
            'guest_wlan_enabled': False,
            'admin_name': 'admin',
            'admin_password': '',
            'create_user_account_is_checked': False,
        },

        @param new_conf = {
            # dhcp_enabled is False, meaning IP config for manual setting is needed
            'dhcp_enabled': False,
            'ip_addr': '192.168.0.2',
            'net_mask': '255.255.255.0',
            'gateway': '192.168.0.253',
            'dns1': '192.168.0.252',

            'wireless1_enabled': True,
            'wireless1_name': 'rat-setup-wizard',
            'authentication_open': True,

            'create_user_account_is_checked': True,
            'new_user_name': 'user',
            'new_user_password': 'password'
        }

        @return: None

        """

        logging.info("Navigate to the ZD's WebUI URL: %s" % self.url)
        self.s.open(self.url)
        self.s.wait_for_page_to_load(self.conf['loadtime_open1'])


        #
        # The ZD's WebUI is expected to be at the Language page
        #
        logging.info("Stand on the Language page")
        self._config_wizard_language(default_conf, new_conf)
        # Move on to the next page
        self.s.click_and_wait(self.info['loc_wzd_next_button'])


        #
        # The ZD's WebUI is expected to be at the General page
        #
        logging.info("Stand on the General page")
        self._config_wizard_system_name(default_conf, new_conf)
        self._config_wizard_country_code(default_conf, new_conf)
        self._config_wizard_mesh_enabled(default_conf, new_conf)
        # Move on to the next page
        self.s.click_and_wait(self.info['loc_wzd_next_button'])


        #
        # The ZD's WebUI is expected to be at the Management IP page
        #
        logging.info("Stand on the Management IP page")
        self._config_wizard_management_ip(default_conf, new_conf)
        # Move on to next page
        self.s.click_and_wait(self.info['loc_wzd_next_button'])


        #
        # The ZD's WebUI is expected to be at the Wireless LANs page
        #
        logging.info("Stand on the Wireless LANs page")
        self._config_wizard_wireless1_enabled(default_conf, new_conf)
        self._config_wizard_guest_wlan_enabled(default_conf, new_conf)
        # Move on to next page
        self.s.click_and_wait(self.info['loc_wzd_next_button'])


        #
        # The ZD's WebUI is expected to be at the Administrator page
        #
        logging.info("Stand on the Admin Name page")
        self._config_wizard_admin_user(default_conf, new_conf)
        self.s.click_and_wait(self.info['loc_wzd_next_button'])


        #
        # The ZD's WebUI is expected to be at the Finish page
        #
        logging.info("Stand on the Finish page")
        self.s.click_and_wait(self.info['loc_wzd_finish_button'], 5)
        
        #@author: chen.tao@ruckuswireless.com since 2014-10-17
        #to fix behavior change: ZF-10299
        if self.s.is_element_present(self.info['loc_wzd_service_term_ckbox']):
            logging.info("Stand on the Service Term page")
            self.s.click_if_not_checked(self.info['loc_wzd_service_term_ckbox'])
            self.s.click_and_wait(self.info['loc_wzd_next_button'])

        #TODO: wait finish complete before refresh zd web, sometime zd will change to setup wizard page, don't know why
        if self.s.is_element_visible("//a[@id='reconnectIpv4Url']") or self.s.is_element_visible("//a[@id='reconnectIpv6Url']"):
            pass
        else:
            raise Exception("Error: cannot finish setup wizard")

        logging.info("Navigate to the Zone Director's homepage: %s" % self.url)
        self.s.open(self.url)
        self.s.wait_for_page_to_load(self.conf['loadtime_open2'])
        self.current_tab = self.LOGIN_PAGE
        
        if not self.s.is_element_present(self.info['loc_login_ok_button']):
            logging.info("Fail to navigate to the ZD's web UI.")
            raise Exception("Error: could not navigate to the original url")

    def _setup_wizard_cfg_totally_followig_defalut_cfg(self, default_conf = {}, new_conf = {},time_out=120):
        """
        only click next in each page

        """
        t0 = time.time()
        while True:
            try:
                logging.info("Navigate to the ZD's WebUI URL: %s" % self.url)
                self.s.open(self.url)
                self.s.wait_for_page_to_load(self.conf['loadtime_open1'])
                break
            except:
                if time.time()-t0>time_out:
                    raise Exception('can not access zd web UI after %s seconds'%time_out)

        #
        # The ZD's WebUI is expected to be at the Language page
        #
        logging.info("Stand on the Language page")
        # Move on to the next page
        self.s.click_and_wait(self.info['loc_wzd_next_button'])
        time.sleep(0.5)


        #
        # The ZD's WebUI is expected to be at the General page
        #
        logging.info("Stand on the General page")
        if new_conf.has_key('mesh_enabled'):
            if new_conf['mesh_enabled']:
                self.s.click_if_not_checked(self.info['loc_wzd_mesh_checkbox'])
        time.sleep(0.5)
        # Move on to the next page
        self.s.click_and_wait(self.info['loc_wzd_next_button'])
        time.sleep(0.5)

        #
        # The ZD's WebUI is expected to be at the Management IP page
        #
        logging.info("Stand on the Management IP page")
        if new_conf.has_key('ip_dualmode'):
            if new_conf['ip_dualmode']:
                self.s.click_if_not_checked(self.info['loc_wzd_ip_dualmode_radio'])
        time.sleep(0.5)
        # Move on to next page
        self.s.click_and_wait(self.info['loc_wzd_next_button'])
        time.sleep(0.5)

        #
        # The ZD's WebUI is expected to be at the Wireless LANs page
        #
        logging.info("Stand on the Wireless LANs page")
        # Move on to next page
        self.s.click_if_checked(self.info['loc_wzd_1st_wlan_checkbox'])
        time.sleep(0.5)
        self.s.click_and_wait(self.info['loc_wzd_next_button'])
        time.sleep(0.5)
        #
        # The ZD's WebUI is expected to be at the Administrator page
        #
        logging.info("Stand on the Admin Name page")
        self._config_wizard_admin_user(default_conf, new_conf)
        self.s.click_and_wait(self.info['loc_wzd_next_button'])
        time.sleep(0.5)

        #
        # The ZD's WebUI is expected to be at the Finish page
        #
        logging.info("Stand on the Finish page")
        self.s.click_and_wait(self.info['loc_wzd_finish_button'], 5)

        #@author: chen.tao@ruckuswireless.com since 2014-10-17
        #to fix behavior change: ZF-10299
        if self.s.is_element_present(self.info['loc_wzd_service_term_ckbox']):
            logging.info("Stand on the Service Term page")
            self.s.click_if_not_checked(self.info['loc_wzd_service_term_ckbox'])
            time.sleep(1)
            self.s.click_and_wait(self.info['loc_wzd_next_button'])

        logging.info("Navigate to the Zone Director's homepage: %s" % self.url)
        self.s.open(self.url)
        self.s.wait_for_page_to_load(self.conf['loadtime_open2'])
        self.current_tab = self.LOGIN_PAGE

        if not self.s.is_element_present(self.info['loc_login_ok_button']):
            logging.info("Fail to navigate to the ZD's web UI.")
            raise Exception("Error: could not navigate to the original url")


    def _delete_all_guestpasses(self):
        """
        This method is used for removing all the guest pass entries from the Generated Guest Passes table

        - Input: none
        - Output: none
        """
        self.login()
        self.navigate_to(self.MONITOR, self.MONITOR_GENERATED_GUESTPASSES)
        while True:
            #PHANNT@20091019 if the button 'Clear All' exists, click it to quickly remove all guest passes
            if self.s.is_element_present(self.info['loc_mon_guestpass_guestdelall_button']):
                self.s.choose_ok_on_next_confirmation()
                self.s.click_and_wait(self.info['loc_mon_guestpass_guestdelall_button'])

            guestpass_total = self._get_total_number(self.info['loc_mon_total_guestpasses_span'],
                                                     "Guestpass_Table")
            guestpass_total = int(guestpass_total)

            if guestpass_total != 0:
                self._delete_element(self.info['loc_mon_guestpass_guestall_checkbox'],
                                     self.info['loc_mon_guestpass_guestdel_button'], "GuestPass")
                #PHANNT@20091019 dynamic sleep amount based on total number of entries
                time.sleep(2 + guestpass_total / 100)

            else:
                logging.info("Deleted all Guest passes in the 'Generated Guest Passes' table successfully")
                break

    def _fill_search_txt(self, loc, txt, wait = 2, is_refresh = False):
        if self._wait_for_element(loc, is_refresh = is_refresh):
            self.s.type_text(loc, txt)
            self.s.type_keys(loc,"\013")
            time.sleep(wait)
        else:
            raise Exception('Element [%s] not found' % loc)
    
    def test_user(self, username, password, guess_db = 'Local Database'):
        """
        Verify if we can use users information to access guestpass generation page on ZD or not.
        Return: True/False
        """
        result = True

        self.navigate_to(self.CONFIGURE, self.CONFIGURE_GUEST_ACCESS, 1)

        self.s.select_option(self.info['loc_cfg_guestaccess_auth_server_option'], guess_db)
        self.s.click_and_wait(self.info['loc_cfg_guestaccess_guestpass_apply_button'])
        guestpass_url = self.s.get_text(self.info['loc_cfg_guestaccess_guestpass_url_span'])

        logging.info("Navigate to the guestpass url: '%s'" % guestpass_url)
        self.s.open(guestpass_url)
        time.sleep(1)
        logging.info("Fill authentication username '%s' and password '%s'" % (username, password))
        self.s.type_text(self.info['loc_guestpass_username_textbox'], username)
        self.s.type_text(self.info['loc_guestpass_password_textbox'], password)
        self.s.click_and_wait(self.info['loc_guestpass_login_button'], 5)

        if self.s.is_element_present(self.info['loc_guestpass_loginfailed_div'], 0.2) or\
           not self.s.is_element_present(self.info['loc_guestinfo_next_button'], 0.2):
            result = False

        self.s.open(self.url)
        self.current_tab = self.LOGIN_PAGE

        return result

    def create_role (self, **kwargs):
        args = {"rolename": "", "specify_wlan": "", "guestpass": True, "description": "",
                "group_attr": "", "zd_admin": ""}
        args.update(kwargs)

        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)
        self.s.click_and_wait(self.info['loc_cfg_roles_createnew_span'])

        self.s.type_text(self.info['loc_cfg_roles_rolename_textbox'], args["rolename"])

        if args["description"]:
            self.s.type_text(self.info['loc_cfg_roles_description_textbox'], args["description"])

        if args["group_attr"]:
            self.s.type_text(self.info['loc_cfg_roles_radius_group_attr_textbox'], args["group_attr"])

        if not args["specify_wlan"]:
            self.s.click_and_wait(self.info['loc_cfg_roles_allow_all_wlans_radio'])

        else:
            self.s.click_and_wait(self.info['loc_cfg_roles_allow_specify_wlans_radio'])
            max_wlan_entries = self.info['const_cfg_roles_max_wlans_entries']
            i = 0
            while i < max_wlan_entries:
                find_checkbox = self.info['loc_cfg_roles_wlans_checkbox'].replace("$_$", str(i + 1))

                if self.s.is_element_present(find_checkbox):
                    find_wlan = self.info['loc_cfg_roles_wlans_label'].replace("$_$", str(i + 1))
                    if self.s.get_text(find_wlan) == args["specify_wlan"]:
                        self.s.click_if_not_checked(find_checkbox)
                        break

                i += 1

        if args["guestpass"]:
            self.s.click_if_not_checked(self.info['loc_cfg_roles_allow_generate_pass_checkbox'])

        else:
            self.s.click_if_checked(self.info['loc_cfg_roles_allow_generate_pass_checkbox'])

        allow_zdadmin_checkbox_loc = self.info["loc_cfg_roles_allow_zd_admin_checkbox"]
        full_admin_priv_radio_loc = self.info["loc_cfg_roles_full_admin_priv_radio"]
        operation_admin_priv_radio_loc = self.info["loc_cfg_roles_operation_admin_priv_radio"]
        limited_admin_priv_radio_loc = self.info["loc_cfg_roles_limited_admin_priv_radio"]
        if args["zd_admin"]:
            if not self.s.is_checked(allow_zdadmin_checkbox_loc):
                self.s.click_and_wait(allow_zdadmin_checkbox_loc)

            if args["zd_admin"] == "full":
                self.s.click_and_wait(full_admin_priv_radio_loc)
                
            elif args["zd_admin"] == "operation":
                self.s.click_and_wait(operation_admin_priv_radio_loc)

            elif args["zd_admin"] == "limited":
                self.s.click_and_wait(limited_admin_priv_radio_loc)

            else:
                raise Exception("Unknown zd_admin option '%s'" % args["zd_admin"])
        else:
            if self.s.is_checked(allow_zdadmin_checkbox_loc):
                self.s.click_and_wait(allow_zdadmin_checkbox_loc)

        self.s.click_and_wait(self.info['loc_cfg_roles_ok_button'])

        # If an alert of wrong configuration(ex: wrong role name, duplicated name...) appears
        # click the Cancel button
        self.s.get_alert(self.info['loc_cfg_roles_cancel_button'])
        logging.info("Create role " + args["rolename"] + " successfully")

    def get_role_cfg_by_name(self, role_name):
        '''
        Output:
            a dict of the role configuration.
                {"role_name": "",
                 "description": "",
                 "group_attr": "",
                 "guest_pass_gen": True/False,
                 "allow_all_wlans": True/False,
                 "specify_wlan_list": [],    #The key won't exist when allow_all_wlans is True
                 "allow_zd_admin": True/False,
                 "zd_admin_mode": "super"/"operator"/"monitoring",    #The key won't exist when allow_zd_admin is False
               }
            None: the role does not exist.
        '''
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)
        if self.s.is_element_present(self.info['loc_cfg_roles_search_text']):
            WGT._fill_search_txt(self.s, self.info['loc_cfg_roles_search_text'], role_name)

        logging.info('Get the configuration of role [%s] from ZD.' % role_name)
        edit_role_span = self.info['loc_cfg_roles_edit_span'] % role_name
        if not self.s.is_element_present(edit_role_span):
            logging.info('The role [%s] does not exist!' % role_name)
            return None

        self.s.click_and_wait(edit_role_span)

        role_cfg = {}
        role_cfg['role_name'] = self.s.get_value(self.info['loc_cfg_roles_rolename_textbox'])
        role_cfg['description'] = self.s.get_value(self.info['loc_cfg_roles_description_textbox'])
        role_cfg['group_attr'] = self.s.get_value(self.info['loc_cfg_roles_radius_group_attr_textbox'])

        if self.s.is_checked(self.info['loc_cfg_roles_allow_generate_pass_checkbox']):
            role_cfg['guest_pass_gen'] = True

        else:
            role_cfg['guest_pass_gen'] = False

        if self.s.is_checked(self.info['loc_cfg_roles_allow_all_wlans_radio']):
            role_cfg['allow_all_wlans'] = True

        elif self.s.is_checked(self.info['loc_cfg_roles_allow_specify_wlans_radio']):
            role_cfg['allow_all_wlans'] = False
            role_cfg['specify_wlan_list'] = []

            max_wlan_entries = self.info['const_cfg_roles_max_wlans_entries']
            i = 1
            while i <= max_wlan_entries:
                find_checkbox = self.info['loc_cfg_roles_wlans_checkbox'].replace("$_$", str(i))
                if self.s.is_element_present(find_checkbox, 3) and self.s.is_checked(find_checkbox):
                    find_wlan = self.info['loc_cfg_roles_wlans_label'].replace("$_$", str(i))
                    role_cfg['specify_wlan_list'].append(self.s.get_text(find_wlan))

                i += 1

        super_admin_radio = self.info['loc_cfg_roles_full_admin_priv_radio']
        operator_admin_radio = self.info['loc_cfg_roles_operator_admin_priv_radio']
        monitoring_admin_radio = self.info['loc_cfg_roles_limited_admin_priv_radio']
        if self.s.is_checked(self.info['loc_cfg_roles_allow_zd_admin_checkbox']):
            role_cfg['allow_zd_admin'] = True
            if self.s.is_element_present(super_admin_radio) and self.s.is_checked(super_admin_radio):
                role_cfg['zd_admin_mode'] = 'super'

            elif self.s.is_element_present(operator_admin_radio) and self.s.is_checked(operator_admin_radio):
                role_cfg['zd_admin_mode'] = 'operator'

            elif self.s.is_element_present(monitoring_admin_radio) and self.s.is_checked(monitoring_admin_radio):
                role_cfg['zd_admin_mode'] = 'monitoring'

        else:
            role_cfg['allow_zd_admin'] = False

        self.s.click_and_wait(self.info['loc_cfg_roles_cancel_button'])
        if self.s.is_element_present(self.info['loc_cfg_roles_search_text']):
            WGT._fill_search_txt(self.s, self.info['loc_cfg_roles_search_text'], '')

        return role_cfg

    def get_role_total_numbers(self):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)
        total_roles = self._get_total_role_entries()
        return total_roles

    def get_role(self):
        """
        Get all role from the roles table
        Output: returns a list of roles
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)

        total_roles = self._get_total_role_entries()
        role_list = []
        i = 0

        if total_roles == 0:
            logging.info("The Roles table is empty")
            return []

        while i < total_roles:
            find_role = self.info['loc_cfg_roles_name_cell']
            find_role = find_role.replace("$_$", str(i + 1))
            role_list.append(self.s.get_text(find_role))
            i += 1

        return role_list

#added by west.li
#edit an existed role
    def edit_role(self, old_rolename, new_rolename):
        self._edit_role(old_rolename, new_rolename)


    def _edit_role(self, old_rolename, new_rolename):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)
        total_roles = self._get_total_role_entries()
        i = 0
        if total_roles == 0:
            logging.info("The Roles table is empty")
            return

        while i < total_roles:
            edit_role = self.info['loc_cfg_roles_edit_span1']
            edit_role = edit_role.replace("$_$", str(i))
            find_role = self.info['loc_cfg_roles_name_cell']
            find_role = find_role.replace("$_$", str(i + 1))
            get_rolename = self.s.get_text(find_role)

            if get_rolename == old_rolename:
                logging.info('role %s found,begin edit'%get_rolename)
                self.s.click_and_wait(edit_role)
                self.s.type_text(self.info['loc_cfg_roles_rolename_textbox'], new_rolename)
                self.s.click_and_wait(self.info['loc_cfg_roles_ok_button'])
                if (self.s.is_alert_present(5)):
                    msg_alert = self.s.get_alert()
                    raise Exception(msg_alert)
                logging.info("Role %s is edit from role %s successfully" % (new_rolename, old_rolename))
                return

            i += 1

        logging.info("The role " + old_rolename + " is not existed in the Roles table")

    def clone_role(self, old_rolename, new_rolename):
        self._clone_role(old_rolename, new_rolename)


    def _clone_role(self, old_rolename, new_rolename):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)
        total_roles = self._get_total_role_entries()
        i = 0
        if total_roles == 0:
            logging.info("The Roles table is empty")
            return

        while i < total_roles:
            clone_role = self.info['loc_cfg_roles_clone_span']
            clone_role = clone_role.replace("$_$", str(i))
            find_role = self.info['loc_cfg_roles_name_cell']
            find_role = find_role.replace("$_$", str(i + 1))
            get_rolename = self.s.get_text(find_role)

            if get_rolename == old_rolename:
                self.s.click_and_wait(clone_role)
                self.s.type_text(self.info['loc_cfg_roles_rolename_textbox'], new_rolename)
                self.s.click_and_wait(self.info['loc_cfg_roles_ok_button'])
                logging.info("Role %s is cloned from role %s successfully" % (new_rolename, old_rolename))
                return

            i += 1

        logging.info("The role " + old_rolename + " is not existed in the Roles table")


    def _get_total_role_entries(self):
        total_roles = 0
        while True:
            traverse_role = self.info['loc_cfg_roles_row']
            traverse_role = traverse_role.replace("$_$", str(total_roles))
            if not self.s.is_element_present(traverse_role):
                break

            total_roles += 1

        return total_roles


    def delete_roles(self, rolename_list):
        for role in rolename_list:
            self._delete_role(role)

    def _delete_role(self, rolename):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)
        total_roles = self._get_total_role_entries()
        i = 0
        if total_roles == 0:
            logging.info("The Roles table is empty")
            return

        while i < total_roles:
            find_role = self.info['loc_cfg_roles_name_cell']
            find_role = find_role.replace("$_$", str(i + 1))
            checkbox = self.info['loc_cfg_roles_role_select_checkbox']
            checkbox = checkbox.replace("$_$", str(i))
            get_rolename = self.s.get_text(find_role)

            if get_rolename == rolename:
                logging.info('role %s find,try to delete'%get_rolename)
                self._delete_element(checkbox, self.info['loc_cfg_roles_delete_button'], "role")
                if (self.s.is_alert_present(5)):
                    msg_alert = self.s.get_alert()
                    raise Exception(msg_alert)

                logging.info("Delete the role " + rolename + " successfully")

                return

            i += 1

        logging.info("The role " + rolename + " is not existed in the Roles table")

        return

    def _delete_all_roles(self):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ROLES)
        if not self.s.is_element_present(self.info['loc_cfg_roles_second_row'], .5):
            logging.info("Roles table only has a Default role now")
            return

        self.s.click_and_wait(self.info['loc_cfg_roles_all_checkbox'])
        self.s.click_if_checked(self.info['loc_cfg_roles_roledefault_checkbox'])

        self.s.choose_ok_on_next_confirmation()
        self.s.click_and_wait(self.info['loc_cfg_roles_delete_button'])
        if not self.s.is_confirmation_present(5):
            raise Exception("No dialog confirmation for deleting all roles appears")

        self.s.get_confirmation()

        if (self.s.is_alert_present(5)):
            msg_alert = self.s.get_alert()
            raise Exception(msg_alert)

        logging.info("Remove all roles from the Roles table successfully")


    def remove_all_roles(self, rolename = ''):
        """
        """
        time.sleep(1)
        if rolename:
            self._delete_role(rolename)

        else:
            self._delete_all_roles()


    def get_zero_it_activate_url(self):
        """
        This function returns the activate url that used for downloading zero-it tool
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS)
        activate_url = self.s.get_text(self.info['loc_cfg_wlans_zeroit_activate_url_span'])

        return activate_url


    def get_zero_it_cfg(self):
        """
        This function returns a name of authentication server
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS, 1)
        zeroit_auth_server = self.info['loc_cfg_wlans_zeroit_auth_server_option']
        if not self.s.is_element_present(zeroit_auth_server):
            raise Exception("Element %s not found" % zeroit_auth_server)

        res = self.s.get_selected_label(zeroit_auth_server)
        time.sleep(1)

        return res


    def _set_zero_it_cfg(self, auth_server):
        """
        This function sets authentication server for zero-it
        @param auth_server: Name of the authentication database
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS, 1)

        self.s.select_option(self.info['loc_cfg_wlans_zeroit_auth_server_option'], auth_server)
        self.s.click_and_wait(self.info['loc_cfg_wlans_zeroit_apply_button'])

        #refresh Web and check ig the value set just now is shown correctly        
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS, 1)
        
        newval = self.s.get_selected_option(self.info['loc_cfg_wlans_zeroit_auth_server_option'])
        if newval != auth_server:
            raise Exception('Element Zero IT auth server value %s changed after Web is refreshed' % auth_server)

    def set_zero_it_cfg(self, auth_server):
        """
        This function sets authentication server for zero-it
        @param auth_server: Name of the authentication database
        """
        self._set_zero_it_cfg(auth_server)


    def _get_total_auth_server(self):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER)
        return self._get_total_number(self.info['loc_cfg_authsvr_total_number_span'], "Authentication Servers")

    def get_total_auth_server(self):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER, 2)
        locator = self.info['loc_cfg_authsvr_total_number_span']
        number_servers = self.s.get_text(locator)
        if not number_servers:
            time.sleep(5)
            number_servers = self.s.get_text(locator)

        time.sleep(1)
        pat = ".*\(([0-9]+)\)$"
        match_obj = re.search(pat, number_servers)
        if match_obj:
            number_servers = match_obj.group(1)

        else:
            raise Exception("Can not get the total number of rows in Authentication Server Table")

        time.sleep(3)

        return number_servers

    def clone_radius_auth_server(self, old_server_name, new_server = "", new_port = "", new_secret = "", new_server_name = ""):
        self._clone_radius_auth_server(old_server_name, new_server, new_port, new_secret, new_server_name)


    def clone_ad_auth_server(self, old_server_name, new_server = "", new_port = "", new_domain = "", new_server_name = ""):
        self._clone_ad_auth_server(old_server_name, new_server, new_port, new_domain, new_server_name)


    def _clone_radius_auth_server(self, old_server_name, new_server = "", new_port = "", new_secret = "", new_server_name = ""):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER)
        auth_serv_total = self._get_total_number(self.info['loc_cfg_authsvr_total_number_span'],
                                                 "Authentication Servers")

        if auth_serv_total == "0": # return immediately if no existed authentication server
            logging.info("There is no existed authentication server in Authentication Server table")
            return

        max_auth_serv_row = int(self.info['const_cfg_authsvr_table_size'])
        row = 1
        i = 0
        # Find server's name on the authentication server table
        while i < int(auth_serv_total):
            find_serv = self.info['loc_cfg_authsvr_name_cell']
            find_serv = find_serv.replace("$_$", str(row))
            clone_server = self.info['loc_cfg_authsvr_clone_span']
            clone_server = clone_server.replace("$_$", str(i))
            get_auth_name = self.s.get_text(find_serv)

            if get_auth_name == old_server_name:
                self.s.click_and_wait(clone_server)
                if new_server_name:
                    self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], new_server_name)

                else:
                    new_server_name = "%s_cloned" % old_server_name
                    self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], new_server_name)

                if new_server:
                    self.s.type_text(self.info['loc_cfg_authsvr_ip_address_textbox'], new_server)

                # If radius server port is different from the default
                if new_port:
                    self.s.type_text(self.info['loc_cfg_authsvr_port_textbox'], new_port)

                if new_secret:
                    self.s.type_text(self.info['loc_cfg_authsvr_pwd_textbox'], new_secret)
                    self.s.type_text(self.info['loc_cfg_authsvr_pwd2_textbox'], new_secret)

                self.s.click_and_wait(self.info['loc_cfg_authsvr_ok_button'])

                # If an alert of wrong configuration(ex: wrong server name, duplicated name) appears
                # click the Cancel button
                self.s.get_alert(self.info['loc_cfg_authsvr_cancel_button'])
                logging.info("Authentication server " + old_server_name + " was cloned successfully")
                return

            if row == max_auth_serv_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_authsvr_next_image'])

            row = row + 1
            i = i + 1
            time.sleep(1)

        logging.info("Authentication server " + old_server_name + " is not existed in the table")


    def _clone_ad_auth_server(self, old_server_name, new_server = "", new_port = "",
                              new_domain = "", new_server_name = ""):

        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER)
        auth_serv_total = self._get_total_number(self.info['loc_cfg_authsvr_total_number_span'],
                                                 "Authentication Servers")

        if auth_serv_total == "0": # return immediately if no existed authentication server
            logging.info("There is no existed authentication server in Authentication Server table")
            return

        max_auth_serv_row = int(self.info['const_cfg_authsvr_table_size'])
        row = 1
        i = 0
        # Find server's name on the authentication server table
        while i < int(auth_serv_total):
            find_serv = self.info['loc_cfg_authsvr_name_cell']
            find_serv = find_serv.replace("$_$", str(row))
            clone_server = self.info['loc_cfg_authsvr_clone_span']
            clone_server = clone_server.replace("$_$", str(i))
            get_auth_name = self.s.get_text(find_serv)

            if get_auth_name == old_server_name:
                self.s.click_and_wait(clone_server)
                if new_server_name:
                    self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], new_server_name)

                else:
                    new_server_name = "%s_cloned" % old_server_name
                    self.s.type_text(self.info['loc_cfg_authsvr_name_textbox'], new_server_name)

                if new_server:
                    self.s.type_text(self.info['loc_cfg_authsvr_ip_address_textbox'], new_server)

                # If radius server port is different from the default
                if new_port:
                    self.s.type_text(self.info['loc_cfg_authsvr_port_textbox'], new_port)

                if new_domain:
                    self.s.type_text(self.info['loc_cfg_authsvr_domain_textbox'], new_domain)
                self.s.click_and_wait(self.info['loc_cfg_authsvr_ok_button'])

                # If an alert of wrong configuration(ex: wrong server name, duplicated name) appears
                # click the Cancel button
                self.s.get_alert(self.info['loc_cfg_authsvr_cancel_button'])
                logging.info("Authentication server " + old_server_name + " was cloned successfully")
                return

            if row == max_auth_serv_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_authsvr_next_image'])

            row = row + 1
            i = i + 1
            time.sleep(1)

        logging.info("Authentication server " + old_server_name + " is not existed in the table")

        return


    def delete_auth_server(self, server_name):
        self._delete_radius_server(server_name)


    def test_authenticate(self, server_name, username, password):
        return self._test_authenticate(server_name, username, password)


    def _test_authenticate(self, server_name, username, password):
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_AUTHENTICATION_SERVER)

        # select server name
        logging.debug("Server Name: %s" % server_name)
        self.s.select_option(self.info['loc_cfg_authsvr_test_authsvr_option'], server_name)
        self.s.type_text(self.info['loc_cfg_authsvr_test_authsvr_username_textbox'], username)
        self.s.type_text(self.info['loc_cfg_authsvr_test_authsvr_password_textbox'], password)

        # click and wait 5 seconds for authenticate process
        self.s.click_and_wait(self.info['loc_cfg_authsvr_test_authsvr_test_button'], 5)
        result = self.s.get_text(self.info['loc_cfg_authsvr_msg_authtest_span'])
        logging.debug(result)

        return result


    def _get_gen_psk_info_attrib_at_col(self, xpath, row):
        return self._get_ap_attrib_at_col(xpath, row)

    def get_all_generated_psks_total_numbers(self, timeout = 10):
        '''
        Get total numbers of DPSKs.
        '''
        self.navigate_to(self.MONITOR, self.MONITOR_GENERATED_PSK_CERTS, 5)
        self._wait_for_element(self.info['loc_mon_total_generated_psk_span'], timeout = timeout)
        total_generated_psk = self._get_total_number(self.info['loc_mon_total_generated_psk_span'],
                                                     "Generated Dynamic-PSK")
        return total_generated_psk

    def get_all_generated_psks_info(self):
        """
        Get all information of all generated PSKs appearing in the Generated Dynamic-PSKs table
        Input: none
        Output:
        - If Generated Dynamic-PSKs table is not empty, return a list of dictionary,
        in there, each dictionary contains all information of each dynamic-PSK
        - If Generated Dynamic-PSKs table is empty, return an empty list
        """
        self.navigate_to(self.MONITOR, self.MONITOR_GENERATED_PSK_CERTS, 2)

        total_generated_psk = self._get_total_number(self.info['loc_mon_total_generated_psk_span'],
                                                     "Generated Dynamic-PSK")
        generated_psk_list = []
        max_row_psks = int(self.info['const_mon_generated_psk_table_size'])
        i = 0
        count = 1

        while i < int(total_generated_psk):
            user = self._get_gen_psk_info_attrib_at_col('loc_mon_generated_psk_user_cell', i)
            mac = self._get_gen_psk_info_attrib_at_col('loc_mon_generated_psk_mac_cell', i)
            wlans = self._get_gen_psk_info_attrib_at_col('loc_mon_generated_psk_wlans_cell', i)
            created_time = self._get_gen_psk_info_attrib_at_col('loc_mon_generated_psk_created_time_cell', i)
            expired_time = self._get_gen_psk_info_attrib_at_col('loc_mon_generated_psk_expired_time_cell', i)

            #An Nguyen, Apr 2012 - add the vlan infomation
            vlan = self._get_gen_psk_info_attrib_at_col('loc_mon_generated_psk_vlan_id', i)
            
            generated_psk_list.append({'user':user, 'mac': mac, 'wlans':wlans, 'vlan': vlan,'created_time': created_time, 'expired_time': expired_time})
            
            if count == max_row_psks:
                count = 0
                self.s.click_and_wait(self.info['loc_mon_generated_psk_next_dpsk_image'])

            i += 1
            count += 1

        return generated_psk_list

    '''
    should use edit_wlan to edit dpsk expiration instead of below method as follow
    
        if zd.get_version() in ['0.0.0.99', '9.9.0.0']:
            new_wlan_cfg = {'ssid':conf['wlan'], 'dpsk_expiration':conf['psk_expiration']}
            edit_wlan(zd, conf['wlan'], new_wlan_cfg)
        else:
            zd.set_dynamic_psk_cfg(conf['psk_expiration'])
    '''
    def set_dynamic_psk_cfg(self, psk_expiration):
        """
        This function sets maximum valid time for dynamic-psk
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS, 2)

        dyn_psk_expiration = self.info['loc_cfg_wlans_dynpsk_expire_option']
        self.s.select_option(dyn_psk_expiration, psk_expiration)
        self.s.click_and_wait(self.info['log_cfg_wlans_dynpsk_apply_button'])


    def get_dynamic_psk_cfg(self):
        """
        This function gets the expired time of dynamic-psk
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS, 1)

        dyn_psk_expiration = self.info['loc_cfg_wlans_dynpsk_expire_option']
        if not self.s.is_element_present(dyn_psk_expiration):
            raise Exception("Element %s not found" % dyn_psk_expiration)

        res = self.s.get_selected_label(dyn_psk_expiration)
        time.sleep(1)

        return res

    def _remove_all_generated_certs(self):
        """
        This function removes all dynamic-certs out of the Generate Dynamic-Certs table
        """
        self.navigate_to(self.MONITOR, self.MONITOR_GENERATED_PSK_CERTS, 2)

        while True:
            total_generated_certs = self._get_total_number(self.info['loc_mon_total_generated_certs_span'],
                                                           "Generated Dynamic-Certs")
            if total_generated_certs != "0":
                self._delete_element(self.info['loc_mon_generated_certs_all_checkbox'],
                                     self.info['loc_mon_generated_certs_delete_button'], "Dynamic-Certs")
                time.sleep(2)

            else:
                break


    def _remove_all_generated_psks(self):
        """
        This function removes all dynamic-PSKs out of the Generate Dynamic-PSKs table
        """
        self.login()
        self.navigate_to(self.MONITOR, self.MONITOR_GENERATED_PSK_CERTS, 2)

        while True:
            #PHANNT@20091019 if the button 'Clear All' exists, click it to quickly remove all PSKs
            if self.s.is_element_present(self.info['loc_mon_generated_psk_delall_button']):
                self.s.choose_ok_on_next_confirmation()
                self.s.click_and_wait(self.info['loc_mon_generated_psk_delall_button'])

                if self.s.is_confirmation_present(5):
                    self.s.get_confirmation()
            try:
                self.refresh()
            except:
                pass

            total_generated_psk = self._get_total_number(self.info['loc_mon_total_generated_psk_span'],
                                                         "Generated Dynamic-PSKs")
            total_generated_psk = int(total_generated_psk)

            if total_generated_psk != 0:
                self._delete_element(self.info['loc_mon_generated_psk_all_checkbox'],
                                     self.info['loc_mon_generated_psk_delete_button'], "Dynamic-PSKs")
                #PHANNT@20091019 dynamic sleep amount based on total number of entries
                time.sleep(2 + total_generated_psk / 100)

            else:
                break


    def clone_wlan(self, current_ssid, new_ssid):
        """
        This function clones the new wlan using the existing wlan
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_WLANS, 2)
        wlan_count = 0
        while True:
            wc = self.info['loc_cfg_wlan_row']
            wc = wc.replace("$_$", str(wlan_count))
            if not self.s.is_element_present(wc):
                break

            wlan_count = wlan_count + 1

        is_cloned = False
        for wlan_row in range(wlan_count):
            find_wlan = self.info['loc_cfg_wlan_cell']
            find_wlan = find_wlan.replace("$_$", str(wlan_row + 1))
            checkbox = self.info['loc_cfg_wlan_checkbox']
            checkbox = checkbox.replace("$_$", str(wlan_row + 1))
            get_ssid = self.s.get_text(find_wlan)

            if get_ssid == current_ssid:
                clone_span = self.info['loc_cfg_wlans_clone_span']
                clone_span = clone_span.replace("$_$", str(wlan_row))
                self.s.click_and_wait(clone_span, 1)
                self.s.type_text(self.info['loc_cfg_ssid_name_textbox'], new_ssid)

                #Serena Tan. 2010.12.7. Behavior change after Toranto 9.1.0.0.7
                if self.s.is_element_present(self.info['loc_cfg_ssid_textbox']):
                    self.s.type_text(self.info['loc_cfg_ssid_textbox'], new_ssid)

                self.s.click_and_wait(self.info['loc_cfg_wlan_ok_button'])

                # If an alert of wrong configuration(ex: wrong wlan name, duplicated name...) appears,
                # click the Cancel button
                self.s.get_alert(self.info['loc_cfg_wlan_cancel_button'])
                is_cloned = True
                logging.info("Create wlan " + new_ssid + " successfully")
                break

            else:
                wlan_row += 1

        if not is_cloned:
            logging.info("Wlan " + new_ssid + " does not exist in the wlan table")


    def _create_map(self, name, map_path, description = '', timeout = 30):
        """
        Create the new map on Zone Director.
        Input:
        - name: name of the map we want to create.
        - map_path: the full path of the image the will be import.
        - description: the description for image.
        - timeout: the timeout for the checking size and importing action of Zone Director.
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MAPS)
        self.s.click_and_wait(self.info['loc_cfg_maps_createnew_span'])
        self.s.type_text(self.info['loc_cfg_maps_name_textbox'], name)
        self.s.type_text(self.info['loc_cfg_maps_browse_textbox'], map_path)
        if description:
            self.s.type_text(self.info['loc_cfg_maps_description_textbox'], description)

        timestart = time.time()
        timerun = time.time() - timestart
        # Waiting for ZD checking the size
        while not self.s.is_visible(self.info['loc_cfg_maps_import_button']) and timerun < timeout:
            timerun = time.time() - timestart
            time.sleep(10)

            if self.s.is_visible(self.info['loc_cfg_maps_error_uploaded_text']):
                message = self.s.get_text(self.info['loc_cfg_maps_error_uploaded_text'])
                self.s.click_and_wait(self.info['loc_cfg_maps_cancel_button'])
                raise Exception('Create map error', message)

        # Do the import map action
        if self.s.is_visible(self.info['loc_cfg_maps_import_button']):
            self.s.click_and_wait(self.info['loc_cfg_maps_import_button'], 10)
            timestart = time.time()
            timerun = time.time() - timestart
            while not self.s.is_visible(self.info['loc_cfg_maps_ok_button']) and timerun < timeout:
                timerun = time.time() - timestart
                time.sleep(10)

            # Confirm the creating new map action
            if self.s.is_visible(self.info['loc_cfg_maps_ok_button']):
                self.s.choose_ok_on_next_confirmation()
                self.s.click_and_wait(self.info['loc_cfg_maps_ok_button'])
                if self.s.is_alert_present(5):
                    message = self.s.get_alert()
                    raise Exception('Create map error', message)

            else:
                raise Exception('Create map error', 'Can\'t upload the map after %d seconds' % timeout)

        else:
            message = 'Can\'t upload the map after %d seconds' % timeout
            self.s.click_and_wait(self.info['loc_cfg_maps_cancel_button'])
            raise Exception('Create map error', message)

        logging.info('Map \'%s\' was created successfully' % name)
 
 #added by west.li
 #edit an existed map  
    def edit_map (self, oldname, newname):
        self._edit_map(oldname, newname)

    def _edit_map (self, oldname, newname):
        """
        change a existed map name 

        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MAPS)

        user_total = self._get_total_number(self.info['loc_cfg_maps_total_number_span'], "maps")
        # If no maps existed, return immediately
        if user_total == u"0":
            logging.info("There's no maps existed in the maps table to edit")
            return
        

        max_map_row = int(self.info['const_cfg_maps_max_row'])
        row = 1
        i = 0
        # Find umap's name on the user table
        while i < int(user_total):
            find_map = self.info['loc_cfg_maps_name_cell']
            find_map = find_map.replace("$_$", str(row))
            edit = self.info['loc_cfg_maps_edit_span']
            edit = edit.replace("$_$", str(i))
            get_map = self.s.get_text(find_map)

            if get_map == oldname:
                self.s.click_and_wait(edit)
                self.s.type_text(self.info['loc_cfg_maps_name_textbox'], newname)
                self.s.click_and_wait(self.info['loc_cfg_maps_ok_button'])
                self.s.get_alert(self.info['loc_cfg_maps_cancel_button'])
                return

            if row == max_map_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_maps_next_image'])

            row = row + 1
            i = i + 1
            time.sleep(1)

    def _delete_map(self, map_name):
        """
        Delete an existing map on the Maps table.
        Input:
        - map_name: name of the map that we want to delete
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MAPS)
        total_maps = int(self._get_total_number(self.info['loc_cfg_maps_total_maps_span'], 'maps'))
        i = 0
        row = 1
        max_map_row = int(self.info['const_cfg_maps_max_row'])
        # Find and detete the existing map
        while i < total_maps:
            map_name_cell = self.info['loc_cfg_maps_name_cell']
            map_name_cell = map_name_cell.replace("$_$", str(row))
            checkbox = self.info['loc_cfg_maps_map_select_checkbox']
            checkbox = checkbox.replace("$_$", str(i))
            get_map_name = self.s.get_text(map_name_cell)

            if get_map_name == map_name:
                self._delete_element(checkbox, self.info['loc_cfg_maps_delete_button'], "map")
                if (self.s.is_alert_present(5)):
                    message = self.s.get_alert()
                    raise Exception('Delete map error', message)

                logging.info("Delete the map " + map_name + " successfully")

                return

            if row == max_map_row:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_maps_next_image'])

            row += 1
            i += 1

        logging.info("The map " + map_name + " does not exist in the maps table")

    def _delete_all_maps(self):
        """
        Delete all maps that existing on Maps table except the Default map.
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MAPS)
        if not self.s.is_element_present(self.info['loc_cfg_maps_second_row']):
            logging.info("Maps table only has a default map now")
            return

        total_maps = int(self._get_total_number(self.info['loc_cfg_maps_total_maps_span'], 'maps'))
        while total_maps > 1:
            self.s.click_and_wait(self.info['loc_cfg_maps_selectall_checkbox'])
            self.s.click_if_checked(self.info['loc_cfg_maps_default_map_checkbox'])

            self.s.choose_ok_on_next_confirmation()
            self.s.click_and_wait(self.info['loc_cfg_maps_delete_button'])
            if self.s.is_confirmation_present(5):
                self.s.get_confirmation()

            if (self.s.is_alert_present(5)):
                msg_alert = self.s.get_alert()
                raise Exception('Delete map error', msg_alert)

            time.sleep(5)
            total_maps = int(self._get_total_number(self.info['loc_cfg_maps_total_maps_span'], 'maps'))

        logging.info("Remove all maps successfully")


    def create_map(self, name, map_path, description = '', timeout = 30):
        """
        Create the new map on Zone Director
        """
        self._create_map(name, map_path, description, timeout)

    def delete_map(self, map_name):
        """
        Delete an existing map on Zone Director
        """
        self._delete_map(map_name)


    def delete_all_maps(self):
        """
        Delete all non-default maps on the Zone Director.
        """
        self._delete_all_maps()


    def get_maps_info(self):
        """
        Return the list of information of the existing map  on maps table include name, description and size.
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MAPS)

        map_total = self._get_total_number(self.info['loc_cfg_maps_total_maps_span'], "maps")
        map_info_list = []
        row = 1
        i = 0
        max_row_map = int(self.info['const_cfg_maps_max_row'])

        while i < int(map_total):
            # Get map name
            map_name = self.info['loc_cfg_maps_name_cell']
            map_name = map_name.replace("$_$", str(row))
            map_name = self.s.get_text(map_name)

            # Get map description
            mapdesc = self.info['loc_cfg_maps_description_cell']
            mapdesc = mapdesc.replace("$_$", str(row))
            mapdesc = self.s.get_text(mapdesc)

            # Get map size
            mapsize = self.info['loc_cfg_maps_size_cell']
            mapsize = mapsize.replace("$_$", str(row))
            mapsize = self.s.get_text(mapsize)

            map_info_list.append({'name': map_name, 'desc': mapdesc, 'size': mapsize})

            if row == max_row_map:
                row = 0
                self.s.click_and_wait(self.info['loc_cfg_maps_next_image'], 2)

            row = row + 1
            i = i + 1

        #self.logout()
        return map_info_list

    def enable_mesh(self, mesh_name = "", mesh_psk = "", generate_psk = False):
        """
        Enable mesh if it has not been enabled.
        Use default mesh name if it is not provided.
        Mesh passphrase will be generated automatically if it is not provided
        @param mesh_name: ESSID of the mesh
        @param mesh_psk: pass-phrase used to establish mesh links between APs
        @param generate_psk: let the ZD to generate the pass-phrase
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MESH, 2)

        config_changed = False

        # Only enable mesh if it has not been enabled
        if not self.s.is_checked(self.info['loc_cfg_mesh_enable_checkbox']):
            self.s.click_and_wait(self.info['loc_cfg_mesh_enable_checkbox'], 2)
            config_changed = True

        if self.s.is_alert_present(5):
            msg = self.s.get_alert()
            logging.error(msg)
            return False,'alert get:%s'%msg
        
        # Apply new mesh name if it is provided
        if mesh_name:
            logging.info("ZD changes [mesh_name %s]" % (mesh_name))
            self.s.type_text(self.info['loc_cfg_mesh_name_textbox'], mesh_name)
            config_changed = True
            time.sleep(1)

        # Apply new mesh pre-share-key if it is provided
        if mesh_psk:
            logging.info("ZD changes [mesh_psk %s]" % (mesh_psk))
            self.s.type_text(self.info['loc_cfg_mesh_psk_textbox'], mesh_psk)
            config_changed = True
            time.sleep(1)

        # Otherwise, generate a new psk
        if generate_psk:
            logging.info("ZD generates new mesh_psk")
            self.s.click_and_wait(self.info['loc_cfg_mesh_psk_generate_button'])
            config_changed = True

        # Finally, apply new change
        if config_changed:
            logging.info("[ZoneDirector ApplyMeshConf]:\n%s" \
                        % (pformat(dict(mesh_name = mesh_name, msh_psk = mesh_psk), indent = 4)))
            self.s.click_and_wait(self.info['loc_cfg_mesh_apply_button'], 2)
            if self.s.is_alert_present(5):
                self.s.get_alert()
            bugme.do_trace('TRACE_RAT_ON_ZD')
            
        return True,'mesh enable success'

    
    def verify_mesh_enable(self):
        """
        verify mesh enabled or not.
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MESH, 2)
        if not self.s.is_checked(self.info['loc_cfg_mesh_enable_checkbox']):
            return False
        else:
            return True
    

    def get_mesh_cfg(self):
        """ Return current mesh configuration
        @return: a dictionary with the following items:
        - mesh_enable: True/False
        - mesh_name: ESSID of the mesh
        - mesh_psk: pass-phrase of the mesh
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MESH, 2)

        mesh_info = {}
        mesh_info['mesh_enable'] = self.s.is_checked(self.info['loc_cfg_mesh_enable_checkbox'])
        # From 9.3 the mesh ssid and mesh psk box will not show if mesh is disabled.
        # Changed to get those values only when mesh is enabled.
        # @an.nguyen@ruckuswireless.com by Nov, 2011
        if mesh_info['mesh_enable']:
            time.sleep(0.5)
            mesh_info['mesh_name'] = self.s.get_value(self.info['loc_cfg_mesh_name_textbox'])
            time.sleep(0.5)
            mesh_info['mesh_psk'] = self.s.get_value(self.info['loc_cfg_mesh_psk_textbox'])
        else:
            mesh_info['mesh_name'] = ''
            mesh_info['mesh_psk'] = ''
            
        return mesh_info


    #Updated by cwang@20130529, Remove postfix tag v5
    def set_abf(self, do_abf = True, rate_limit = None):
        """
        Configure ABF for 9.5 and build after 9.5
        @param do_abf: enable or disable ABF
        @param rate_limit: the value to set after enabling ABF, no need to set in 9.5
        """
        
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_MESH, 2)
        
        config_changed = False
        if do_abf:
            if not self.s.is_checked(self.info['loc_cfg_abf_enable_checkbox']):
                logging.info("Enable ABF")
                self.s.click_and_wait(self.info['loc_cfg_abf_enable_checkbox'], 2)
                config_changed = True
            else:
                pass
        else:
            if self.s.is_checked(self.info['loc_cfg_abf_enable_checkbox']):
                logging.info("Disable ABF")
                self.s.click_and_wait(self.info['loc_cfg_abf_enable_checkbox'], 2)
                config_changed = True
            else:
                pass
        if config_changed:
            logging.info("Apply ABF configuration")
            self.s.click_and_wait(self.info['loc_cfg_abf_apply_button'], 2)
            if self.s.is_alert_present(5):
                self.s.get_alert()
            bugme.do_trace('TRACE_RAT_ON_ZD')

    def verify_pif_rate_limit(self, expected_status = False, expected_rate_limit = None):
        """
        Check PIF rate limit settings
        @param expected_status: the status expect PIF rate limit to be currently, on or off
        @param expected_rate_limit: the value expect limiting rate to be when PIF rate limit is on
        """
        
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SERVICES, 2)
        
        if expected_status:
            logging.info("Check if PIF rate limit is enabled")
            if not self.s.is_checked(self.info['loc_cfg_pif_rate_limit_enable_checkbox']):
                return False
            else:
                if expected_rate_limit is not None:
                    logging.info("Check if the value of limiting rate is as expected")
                    current_value = self.s.get_value(self.info['loc_cfg_pif_rate_limit_textbox'], 5)
                    if int(current_value) != expected_rate_limit:
                        return False
        else:
            logging.info("Check if PIF rate limit is disabled")
            if self.s.is_checked(self.info['loc_cfg_pif_rate_limit_enable_checkbox']):
                return False
        
        return True

    def set_pif_rate_limit(self, expected_status = False, expected_rate_limit = None):
        """
        Configure PIF rate limit
        @param expected_status: enable or disable PIF rate limit
        @param expected_rate_limit: the value of limiting rate to be set after enabling PIF rate limit
        """
        
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SERVICES, 2)
        
        config_changed = False
        if expected_status:
            if not self.s.is_checked(self.info['loc_cfg_pif_rate_limit_enable_checkbox']):
                logging.info("Enable PIF rate limit")
                self.s.click_and_wait(self.info['loc_cfg_pif_rate_limit_enable_checkbox'], 2)
                config_changed = True
            else:
                pass
            logging.info("Set the value of limiting rate")
            self.s.type_text(self.info['loc_cfg_pif_rate_limit_textbox'], expected_rate_limit)
            config_changed = True
            time.sleep(2)
        else:
            if self.s.is_checked(self.info['loc_cfg_pif_rate_limit_enable_checkbox']):
                logging.info("Disable PIF rate limit")
                self.s.click_and_wait(self.info['loc_cfg_pif_rate_limit_enable_checkbox'], 2)
                config_changed = True
            else:
                pass
        if config_changed:
            logging.info("Apply PIF rate limit configuration")
            self.s.click_and_wait(self.info['loc_cfg_pif_rate_limit_apply_button'], 2)
            if self.s.is_alert_present(5):
                self.s.get_alert()
                return False
        
        return True

    def get_admin_cfg(self):
        """ 
        Return current configuration of administrator account
        @return: a dictionary with the following keys:
        'auth_by_local': a boolean value (available on Odessa)
        'auth_by_external': a boolean value (available on Odessa)
        'auth_server': external authentication server (available on Odessa)
        'fallback_local': a boolean value (available on Odessa)
        'admin_name': a string represents the name of the Administrator account
        'admin_pass1': a string represents the password of the account
        'admin_pass2': a string represents the password of the account
        """
        self.navigate_to(self.ADMIN, self.ADMIN_PREFERENCE)

        x = {}
        if self.s.is_element_present(self.info['loc_admin_preference_auth_local_radio']):
            if self.s.is_checked(self.info['loc_admin_preference_auth_local_radio']):
                x['auth_method'] = "local"

        if self.s.is_element_present(self.info['loc_admin_preference_auth_external_radio']):
            if self.s.is_checked(self.info['loc_admin_preference_auth_external_radio']):
                x['auth_method'] = "external"

        if self.s.is_element_present(self.info['loc_admin_preference_auth_server_option']) and \
           self.s.is_editable(self.info['loc_admin_preference_auth_server_option']):
            x['auth_server'] = self.s.get_selected_label(self.info['loc_admin_preference_auth_server_option'])

        if self.s.is_element_present(self.info['loc_admin_preference_fallback_local_checkbox']) and \
           self.s.is_editable(self.info['loc_admin_preference_fallback_local_checkbox']):
            if self.s.is_checked(self.info['loc_admin_preference_fallback_local_checkbox']):
                x['fallback_local'] = True

            else:
                x['fallback_local'] = False

        if self.s.is_editable(self.info['loc_admin_preference_admin_name_textbox']):
            x['admin_name'] = self.s.get_value(self.info['loc_admin_preference_admin_name_textbox'])
            # These textboxes contain unreadable characters --> it is not necessary to read them
            # It is up to the caller to fill in these fields with readable characters
            x['admin_old_pass'] = x['admin_pass1'] = x['admin_pass2'] = ""
#        if self.s.is_editable(self.info['loc_admin_preference_admin_pass1_textbox']):
#            x['admin_pass1'] = self.s.get_value(self.info['loc_admin_preference_admin_pass1_textbox'])
#        if self.s.is_editable(self.info['loc_admin_preference_admin_pass2_textbox']):
#            x['admin_pass2'] = self.s.get_value(self.info['loc_admin_preference_admin_pass2_textbox'])

        return x


    def set_admin_cfg(self, conf):
        """
        Configure the administrator account with given settings
        """
        self.navigate_to(self.ADMIN, self.ADMIN_PREFERENCE)

        if conf.has_key('auth_method'):
            time.sleep(0.5)
            if conf['auth_method'] == "local":
                self.s.click_and_wait(self.info['loc_admin_preference_auth_local_radio'])

            elif conf['auth_method'] == "external":
                self.s.click_and_wait(self.info['loc_admin_preference_auth_external_radio'])

            time.sleep(0.5)

        if conf.has_key('auth_server') and conf['auth_server']:
            self.s.select_option(self.info['loc_admin_preference_auth_server_option'], conf['auth_server'])
            time.sleep(1)

        if conf.has_key('fallback_local'):
            if conf['fallback_local']:
                if not self.s.is_checked(self.info['loc_admin_preference_fallback_local_checkbox']):
                    self.s.click_and_wait(self.info['loc_admin_preference_fallback_local_checkbox'])

            else:
                if self.s.is_checked(self.info['loc_admin_preference_fallback_local_checkbox']):
                    self.s.click_and_wait(self.info['loc_admin_preference_fallback_local_checkbox'])

            time.sleep(0.5)

        if conf.has_key('admin_name'):
            self.s.type_text(self.info['loc_admin_preference_admin_name_textbox'], conf['admin_name'])

        if conf.has_key('admin_old_pass'):
            self.s.type_text(self.info['loc_admin_preference_admin_old_pass_textbox'], conf['admin_old_pass'])

        if conf.has_key('admin_pass1'):
            self.s.type_text(self.info['loc_admin_preference_admin_pass1_textbox'], conf['admin_pass1'])

        if conf.has_key('admin_pass2'):
            self.s.type_text(self.info['loc_admin_preference_admin_pass2_textbox'], conf['admin_pass2'])

        self.s.click_and_wait(self.info['loc_admin_preference_apply_button'])

        if self.s.is_alert_present(5):
            msg = self.s.get_alert()
            raise Exception(msg)

        #Refresh and check value shown on WebUI again
        if conf.has_key('auth_server') and conf['auth_server']:
            self.navigate_to(self.ADMIN, self.ADMIN_PREFERENCE)
            newval = self.s.get_selected_option(self.info['loc_admin_preference_auth_server_option'])
            if newval != conf['auth_server']:
                raise Exception('Element administer validation server value %s changed after Web is refreshed' % conf['auth_server'])


    def get_mac_address(self):
        """ Return the MAC address of the Zone Director """
        self.navigate_to(self.DASHBOARD, self.NOMENU, 2)

        return self.s.get_text(self.info['loc_dashboard_sysinfo_mac_cell'])


    def delete_clients(self, mac_string):
        """
        Search and delete the existing clients whose mac address includes  in 'Currently Active Clients' page.
        Input:
            mac_string: a regular string is a part of or a full mac address.
        """
        self.navigate_to(self.MONITOR, self.MONITOR_CURRENTLY_ACTIVE_CLIENTS)
        self.s.click_and_wait(self.info['loc_mon_clients_refresh_image'], 2)

        # Search the expected client base on the mac address
        self.s.type_keys(self.info['loc_mon_clients_search_textbox'], mac_string.lower())
        time.sleep(2)

        # Get the total number of clients in search result
        total_clients = self._get_total_number(self.info['loc_mon_clients_total_number_span'], "Current Active Clients")

        # Delete all clients if they existed
        if int(total_clients) > 0:
            first_client_span = self.info['loc_mon_clients_delete_span'].replace("$_$", "0")
            for i in range(int(total_clients)):
                self.s.click_and_wait(first_client_span)

            logging.info("Delete %s active clients with [%s] in mac address successfully" % (total_clients, mac_string))

        else:
            logging.info('"Current Active Clients" table does not have any client with [%s] in mac address' % mac_string)


    def block_clients(self, mac_string):
        """
        Search and block the existing clients whose mac address includes  in 'Currently Active Clients' page.
        Input:
            mac_string: a regular string is a part of or a full mac address.
        """
        self.navigate_to(self.MONITOR, self.MONITOR_CURRENTLY_ACTIVE_CLIENTS)
        self.s.click_and_wait(self.info['loc_mon_clients_refresh_image'], 2)

        # Search the expected client base on the mac address
        self.s.type_keys(self.info['loc_mon_clients_search_textbox'], mac_string.lower())
        time.sleep(2)

        # Get the total number of clients in search result
        total_clients = self._get_total_number(self.info['loc_mon_clients_total_number_span'], "Current Active Clients")
        # Block all clients if they existed
        if int(total_clients) > 0:
            first_client_span = self.info['loc_mon_clients_block_span'].replace("$_$", "0")
            for i in range(int(total_clients)):
                self.s.click_and_wait(first_client_span)

            logging.info("Block %s active clients with [%s] in mac address successfully" % (total_clients, mac_string))

        else:
            logging.info('"Current Active Clients" table does not have any client with [%s] in mac address' % mac_string)


    def unblock_clients(self, mac_string):
        """
        Search and block the existing clients whose mac address includes  in 'Blocked Clients' table.
        Input:
            mac_string: a regular string is a part of or a full mac address.
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_CONTROLS, 2)

        # Search the expected client base on the mac address
        self.s.type_keys(self.info['loc_cfg_blocked_client_search_textbox'], mac_string.lower())
        time.sleep(2)

        # Get the total number of clients in search result
        total_clients = self._get_total_number(self.info['loc_cfg_total_blocked_client_span'], 'Blocked Clients')
        # UnBlock all clients if they existed
        if int(total_clients) > 0:
            select_all_checkbox = self.info['loc_cfg_blocked_client_all_checkbox']
            unblock_button = self.info['loc_cfg_blocked_client_unblock_button']
            self._delete_element(select_all_checkbox, unblock_button, "Blocked Clients")
            time.sleep(1)

            logging.info("Unblock %s active clients with [%s] in mac address successfully" % (total_clients, mac_string))

        else:
            logging.info('"Blocked Clients" table does not have any client with [%s] in mac address' % mac_string)


    def set_dhcp_server(self, config):
        """
        Do the configuration on DHCP Server field.
        Input:
            config: Dictionary of DHCP Server option:
                - start_ip: the starting ip value that will be set
                - number_ip: the ip range value that will be set
                - leasetime: the lease time information that will be set
                - enable: True/False - Enable/Disable DHCP server on the Zone Director
        """
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)
        if not self.s.is_element_present(self.info['loc_cfg_system_dhcps_fieldset']):
            raise Exception('The DHCP Server configurate field is invisible')

        else:
            enable_checkbox = self.info['loc_cfg_system_dhcps_enable_checkbox']
            enable_server = False if not config.has_key('enable') else config['enable']

            if not enable_server:
                # Uncheck the enable DHCPs server checkbox
                if self.s.is_checked(enable_checkbox):
                    self.s.click_and_wait(enable_checkbox)

                # Click apply button
                self.s.click_and_wait(self.info['loc_cfg_system_dhcps_apply_button'], 3)

                return

            # Check the enable DHCPs server checkbox
            if not self.s.is_checked(enable_checkbox):
                self.s.click_and_wait(enable_checkbox)

            # Set starting ip value
            if config.has_key('start_ip'):
                self.s.type_text(self.info['loc_cfg_system_dhcps_starting_ip_textbox'], config['start_ip'])

            # Set ip range value
            if config.has_key('number_ip'):
                self.s.type_text(self.info['loc_cfg_system_dhcps_number_ip_textbox'], str(config['number_ip']))

            # Set lease time value
            if config.has_key('leasetime'):
                self.s.select_option(self.info['loc_cfg_system_dhcps_leasetime_options'], config['leasetime'])

            # Click 'Cancel' on the confirmation dialog to ZD do nothing if not ZD will auto correct the setting value.
            self.s.choose_cancel_on_next_confirmation()
            # Click apply button
            self.s.click_and_wait(self.info['loc_cfg_system_dhcps_apply_button'], 3)
            msg = ''
            # The ZD will be genarate an alert or an confirm dialog if there are any invalid or wrong setting value is setted.
            # Get any exist alert message
            if self.s.is_alert_present(5):
                msg = self.s.get_alert()

            # Get any confirmation message
            elif self.s.is_confirmation_present(5):
                msg = self.s.get_confirmation()

            if msg:
                raise Exception(msg)


    def get_assigned_ip_info(self, expect_info = ''):
        """
        Return the assigned ip information of the ZD DHCP Server.
        Input:
            expect_info: Mac address or IP address of the client. If None return all information we have.
        Output:
            The list of dictionary of assigned IP information.
            Ex. [{'ip': u'192.168.0.12', 'mac': u'00:1f:41:16:3f:10', 'leasetime': u'2008/11/14  04:45:25'}]
        """
        assigned_info = []
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)
        if not self.s.is_visible(self.info['loc_cfg_system_dhcps_fieldset']):
            logging.info('The DHCP Server configurate field is invisible')

        else:
            # Click on the 'click here' link to show the assigned IP table
            try_click = 5
            show_link = self.info['loc_cfg_system_dhcps_assigned_showlink']
            assigned_table = self.info['loc_cfg_system_dhcps_assigned_table']
            for i in range(try_click):
                if self.s.is_element_present(show_link):
                    self.s.click_and_wait(show_link)

                if self.s.is_visible(assigned_table):
                    break

            time.sleep(5)
            if not self.s.is_visible(assigned_table):
                raise Exception('The assigned IP table could not be showed')

            else:
                # Find the appropriate information relating with expected info (if it exists)
                if expect_info:
                    search_textbox = self.info['loc_cfg_system_dhcps_search_textbox']
                    # In selenium, therefore some reason the '.' is not be set in type_keys function.
                    self.s.type_text(search_textbox, expect_info) # Just copy - paste the value, we need send more an key type action.
                    self.s.type_keys(search_textbox, '.') # In Selenium the type_keys([area], '.') do an type key action but does not send the '.' value.
                    time.sleep(2)

                total_span = self.info['loc_cfg_system_dhcps_assigned_total_span']
                total_ip = int(self._get_total_number(total_span, 'Assigned IP Table'))

                if total_ip > 0:
                    info = {}
                    max_row_user = 15
                    i = 0
                    row = 1
                    while i < total_ip:
                        mac_cell = self.info['loc_cfg_system_dhcps_assigned_mac_cell'].replace('$_$', str(i))
                        ip_cell = self.info['loc_cfg_system_dhcps_assigned_ip_cell'].replace('$_$', str(i))
                        leasetime_cell = self.info['loc_cfg_system_dhcps_assigned_leasetime_cell'].replace('$_$', str(i))
                        info['mac'] = self.s.get_text(mac_cell)
                        info['ip'] = self.s.get_text(ip_cell)
                        info['leasetime'] = self.s.get_text(leasetime_cell)
                        assigned_info.append(info.copy())

                        if row == max_row_user:
                            row = 0
                            self.s.click_and_wait(self.info['loc_cfg_user_next_image'])

                        row = row + 1
                        i = i + 1

        return assigned_info


    def get_dhcp_server_info(self):
        """
        Return the current configuration of ZD DHCP server.
        Return:
            Dictionary of DHCP server infomation.
            Ex. {'start_ip':'', 'number_ip':'', 'leasetime':'', 'start_server':''}
        """
        server_info = {}
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_SYSTEM, 2)
        if not self.s.is_visible(self.info['loc_cfg_system_dhcps_fieldset']):
            logging.info('The DHCP Server configuration field is invisible')

        else:
            server_info['enable'] = self.s.is_checked(self.info['loc_cfg_system_dhcps_enable_checkbox'])
            if server_info['enable']:
                server_info['start_ip'] = self.s.get_value(self.info['loc_cfg_system_dhcps_starting_ip_textbox'])
                server_info['number_ip'] = self.s.get_value(self.info['loc_cfg_system_dhcps_number_ip_textbox'])
                server_info['leasetime'] = self.s.get_selected_label(self.info['loc_cfg_system_dhcps_leasetime_options'])

        return server_info


    def restart_aps(self, mac_addr = ''):
        """
        WARNING: OBSOLETE
        . please use lib.zd.aps.reboot_all_aps or reboot_ap_by_mac_addr fns

        This function click restart buttion at Monitor/Access Points page to restart
        the AP.
        Input:
        - mac_addr: mac address of AP will be restart. If not, will restart all AP
        """
        if mac_addr:
            return APS.reboot_ap_by_mac_addr(self, mac_addr)

        return APS.reboot_all_aps(self)
    
    #Jacky.Luh update by 2012-06-26
    def click_mon_apsummary_refresh(self):
        """
        This funtion click the refresh button of apsummary
        """
        return APS.click_mon_apsummary_refresh(self)
    
    
    def set_session_timeout(self,timeout):
        self.navigate_to(self.ADMIN, self.ADMIN_PREFERENCE)
        self.s.type_text(self.info['loc_admin_preference_idle_timeout_textbox'],str(timeout))
        self.s.click_and_wait(self.info['loc_admin_preference_idle_timeout_apply_button'])
        msg='set timeout %s successfully,no confirmation,no alert'%timeout 
        if self.s.is_confirmation_present(5):
            confirmation=self.s.get_confirmation()
            logging.info("Got confirmation: %s" % confirmation)
            msg='set timeout %s successfully'%timeout 
        if self.s.is_alert_present():
            alert=self.s.get_alert()
            logging.info("Got alert: %s" % alert)
            if 'Timeout interval must be a number between 1 and 1440' in alert and\
            (timeout<1 or timeout>1440):
                msg='correct behavior,timeout %s can not be set'%timeout
                logging.info(msg)
                return True,msg
        if timeout<1 or timeout>1440:
            msg='wrong behavior,timeout %s can be set and no alert'%timeout
            logging.info(msg)
            return False,msg
        self.login()
        return True,msg
            
    def authenticate_use_admin(self,username='admin',oldpass='admin',newpass='admin'):
        admin_auth_cfg = {"auth_method": "local",
                          "admin_name": username,
                          'admin_old_pass':oldpass,
                          "admin_pass1": newpass,
                          "admin_pass2": newpass}
        self.set_admin_cfg(admin_auth_cfg)
        self.username=username
        self.password=newpass
        self.login()
    
    def get_session_timeout(self):
        self.navigate_to(self.ADMIN, self.ADMIN_PREFERENCE)
        value=self.s.get_value(self.info['loc_admin_preference_idle_timeout_textbox'])
        return int(value)
    
    def check_auto_logout_status(self,expected_status=True):
        self.refresh()
        if self.s.is_element_present(self.info['LoginUsernameTxt'])\
        and self.s.is_element_present(self.info['LoginPasswordTxt']):
            status = True
        elif self.is_logged_in():
            status = False
        else:
            raise('wrong web UI status')
        if expected_status==status:
            return True
        else:
            return False
        
    def configure_telnet_server(self,enable=True,timeout=0.5):
        self.navigate_to(self.CONFIGURE,self.CONFIGURE_SYSTEM)
        self.refresh()
        #Updated by cwang@20121210 for bug fixed. 
        if self.s.is_element_present(self.info['loc_cfg_network_management_icon_collapse']):
            self.s.click_and_wait(self.info['loc_cfg_network_management_icon_collapse'])
        
        if enable:
            self.s.click_if_not_checked(self.info['loc_cfg_enable_telnet_checkbox'],timeout)
        else:
            self.s.click_if_checked(self.info['loc_cfg_enable_telnet_checkbox'],timeout)
        self.s.click(self.info['loc_cfg_enable_telnet_apply_button'])
        logging.info('zd telnet server configure successfully %s'%enable)
        
    #
    # Management VLAN
    #
    def load_mgmt_vlan_info(self):
        logging.info("Checking ZoneDirector has Management VLAN installed or not.")
        self.navigate_to(self.CONFIGURE, self.CONFIGURE_ACCESS_POINT)
        self.has_mgmt_vlan = self.s.is_element_present(self.info['loc_cfg_appolicy_mgmt_vlan_header'])

        self.navigate_to(self.MONITOR, self.MONITOR_ACCESS_POINTS)
        self.has_device_name_at_current_managed_aps = self.s.is_element_present(self.info['loc_mon_aps_device_name'])

        if not self.has_mgmt_vlan and not self.has_device_name_at_current_managed_aps:
            logging.info("ZoneDirector does not have Management VLAN installed and Device Name column in APs Summary.")
            return

        logging.info("ZoneDirector has Management VLAN installed. Loading its widgets' locators.")
        self.mgmt_vlan = MVLAN.get_node_mgmt_vlan_info(self)
        logging.info('MGMTVLAN:\n%s' % (pformat(self.mgmt_vlan, indent = 4)))


    def touch_page_load_time(self):
        # support Scaling tests which ZD might be running Virtual Machine
        if self.conf.has_key('x_loadtime') and float(self.conf['x_loadtime']) > 1.0:
            for x in [y for y in self.conf.keys() if re.match(r'^loadtime_', y)]:
                o_val = self.conf[x]
                self.conf[x] = int(self.conf[x] * float(self.conf['x_loadtime']))
                logging.info("Increase %s from [%s ms] to [%s ms]" % (x, str(o_val), str(self.conf[x])))


    def say_hello(self):
        '''
        This is to test the FeatureUpdater
        '''
        print "ZoneDirector2: Hello!"


    def features_adding(self):
        '''
        Define a dict of original/updated attributes
        '''
        return {
        }


    def accumulate_attrs(self):
        '''
        Updates additional attributes
        '''
        for ver, attrs in self.features_adding().iteritems():
            if self.feature_update.has_key(ver):
                self.feature_update[ver].update(attrs)

            else:
                self.feature_update[ver] = attrs



from RuckusAutoTest.common.SeleniumControl import SeleniumManager
class ZoneDirector(ZoneDirector2):

    def __init__(self, config):
        cfg = dict(
            ip_addr = '192.168.0.2',
            username = 'admin',
            password = 'admin',
            model = 'zd',
            browser_type = 'firefox',
            init_s = True,
        )
        cfg.update(config)
        ZoneDirector2.__init__(self, cfg.pop('selenium_mgr', SeleniumManager()),
                               cfg['browser_type'], cfg['ip_addr'],
                               cfg, cfg.pop('https', True))

        self.prepare_feature()
        WebUI.update_feature(self)


    def prepare_feature(self):
        #Update by cwang@2012/6/16.        
        self.feature_update_add = (
        )
        my_ver = self.get_version()              
        for (ver, _dd) in self.feature_update_add:
            if self.feature_update.has_key(ver):
                self.feature_update[ver].update(_dd)

            else:
                self.feature_update[ver] = _dd

            if my_ver.startswith(ver):
                logging.info('Update DONE.')
                break
        
    # The verifyComponent() method is defined, so it will not be added again.
    # Other methods that are listed in the func_map will be attached to the ZoneDirector.
    def verifyComponent(self):
        return self.verify_component()

func_map = {
    'verifyComponent': 'verify_component',
    'configWlan': 'cfg_wlan',
    'removeWlan': 'remove_wlan',
    'removeAllWlan': 'remove_all_wlan',
    'getWlanlist': 'get_wlan_list',
    'removeAllConfig': 'remove_all_cfg',
    'upgradeSW': 'upgrade_sw',
    'setAPPolicyApproval': 'set_ap_policy_approval',
    'getAPPolicyApproval': 'get_ap_policy_approval',
    'allowAPJoining': 'allow_ap_joining',
    'removeApprovalAP': 'remove_approval_ap',
    'configNTP': 'cfg_ntp',
    'getCurrentTime': 'get_current_time',
    'getNTPConfig': 'get_ntp_cfg',
    'getAllAPsInfo': 'get_all_ap_info',
    'getAllAPsSymDict': 'get_all_ap_sym_dict',
    'clearAllAlarms': 'clear_all_alarms',
    'getAlarms': 'get_alarms',
    'clearAllEvents': 'clear_all_events',
    'configSyslogSrv': 'cfg_syslog_server',
    'getSystemName': 'get_system_name',
    'setSystemName': 'set_system_name',
    'getIPConfiguration': 'get_ip_cfg',
    'setIPConfiguration': 'set_ip_cfg',
    'getIPConfigurationStatus': 'get_ip_cfg_status',
    'setIPConfigurationStatus': 'set_ip_cfg_status',
    'setupWizardConfiguration': 'setup_wizard_cfg',
    'getSerialNumber': 'get_serial_number',
    'createRadiusServ': 'create_radius_server',
    'createADServ': 'create_ad_server',
    'removeAllAuthServers': 'remove_all_auth_servers',
    'removeAllUsers': 'remove_all_users',
    'createUser': 'create_user',
    'getNumberUsers': 'get_number_users',
    'deleteUser': 'delete_user',
    'removeAllGuestPasses': 'remove_all_guestpasses',
    'generateGuestPass': 'generate_guestpass',
    'getEvents': 'get_events',
    'setAlarmEmail': 'set_alarm_email',
    'setGuestAccessPolicy': 'set_guestaccess_policy',
    'getGuestAccess': 'get_guestaccess_policy',
    'setGuestPassPolicy': 'set_guestpass_policy',
    'getGuestPassPolicy': 'get_guestpass_policy',
    'setRestrictedSubnets': 'set_restricted_subnets',
    'getRestrictedSubnets': 'get_restricted_subnets',
    'removeRogueAPs': 'remove_rogue_aps',
    'getAllACLNames': 'get_all_acl_names',
    'getACLInfo': 'get_acl_info',
    'createACLRule': 'create_acl_rule',
    'editACLRule': 'edit_acl_rule',
    'removeAllACLRules': 'remove_all_acl_rules',
    'setCountryCode': 'set_country_code',
    'getCountryCode': 'get_country_code',
    '_getTotalNumber': '_get_total_number',
    'gotoLoginPage': 'goto_login_page',
    'getUser': 'get_user',
    'cloneUser': 'clone_user',
    '_getVersion': '_get_version',
    'getAPInfoEx': 'get_ap_info_ex',
    '_deleteAP': '_delete_ap',
    'setAPConfiguration': 'set_ap_cfg',
    'getAPConfiguration': 'get_ap_cfg',
    'getActiveClientList': 'get_active_client_list',
    'removeAllActiveClients': 'remove_all_active_clients',
    '_resetFactory': '_reset_factory',
    '_resetFactoryWaitForAlive_s1': '_reset_factory_wait_for_alive_s1',
    '_resetFactoryWaitForAlive_s2': '_reset_factory_wait_for_alive_s2',
    '_setupWizardConfiguration': '_setup_wizard_cfg',
    'testUser': 'test_user',
    'createRole': 'create_role',
    'getRole': 'get_role',
    'cloneRole': 'clone_role',
    'removeAllRoles': 'remove_all_roles',
    'getZeroITActivateUrl': 'get_zero_it_activate_url',
    'getZeroITConfig': 'get_zero_it_cfg',
    'setZeroITConfig': 'set_zero_it_cfg',
    'getTotalAuthServer': 'get_total_auth_server',
    'cloneRadiusAuthServer': 'clone_radius_auth_server',
    'cloneADAuthServer': 'clone_ad_auth_server',
    'deleteAuthServ': 'delete_auth_server',
    'testAuthenticate': 'test_authenticate',
    'getAllGeneratedPSKsInfo': 'get_all_generated_psks_info',
    'setDynamicPSKConfig': 'set_dynamic_psk_cfg',
    'getDynamicPSKConfig': 'get_dynamic_psk_cfg',
    '_removeAllGeneratedPSKs': '_remove_all_generated_psks',
    'cloneWlan': 'clone_wlan',
    'createMap': 'create_map',
    'deleteMap': 'delete_map',
    'deleteAllMaps': 'delete_all_maps',
    'getMapsInfo': 'get_maps_info',
    'enableMesh': 'enable_mesh',
    'getMeshConfiguration': 'get_mesh_cfg',
    'getAdministratorConfiguration': 'get_admin_cfg',
    'setAdministratorConfiguration': 'set_admin_cfg',
    'getMacAddress': 'get_mac_address',
    'deleteClients': 'delete_clients',
    'blockClients': 'block_clients',
    'unblockClients': 'unblock_clients',
    'setDHCPServer': 'set_dhcp_server',
    'getAssignedIPInfo': 'get_assigned_ip_info',
    'getDHCPServerInfo': 'get_dhcp_server_info',
    'restartAPs': 'restart_aps',
    'loadMgmtVlanInfo': 'load_mgmt_vlan_info',
    'touchPageLoadtime': 'touch_page_load_time',

}

for attr, attr2 in func_map.items():
    # dynamically attaches the new methods to ZoneDirector from ZoneDirector2
    # if they do not exist
    try:
        getattr(ZoneDirector, attr)

    except:
        setattr(ZoneDirector, attr, getattr(ZoneDirector, attr2))

