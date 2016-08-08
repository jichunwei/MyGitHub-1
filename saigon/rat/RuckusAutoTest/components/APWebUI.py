# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
This is the Ruckus AP WebUI component
NOTE: Maintenance > Support Info: need more time to load
"""
import time
import logging
import traceback

from RuckusAutoTest.common.utils import find_key
from RuckusAutoTest.components.WebUI import WebUI

'''
NOTE: the Wireless pages of AP implements a value-assigning technique
after page loaded. This causes the is/check_element_present works fine but fail to
click on these buttons. Adding a sleep here to overcome this problem.
'''
WLAN_PAGE_LOAD_WAIT = 3 # secs


class APWebUI(WebUI):
    """ Static Properties
    These static properties are needed to be overrided in every single class.

    resource_file: is the resource file location, set it to None where there is no resource file
    resource:     is the place holder for loaded resource data, this must be inited as None
    """
    resource_file = 'RuckusAutoTest.components.resources.APWebUIResource'
    resource = None

    username = 'super'
    password = 'sp-admin'

    status_device_ths = [
        'name', 'location', 'gps', 'mac', 'serial', 'firmware', 'uptime',
        'cur_time'
    ]

    device = dict(
        device_name = 'RuckusAP',
    )

    access_mgmt = dict(
        telnet_enabled = 'disabled',
        telnet_port = 23,
        ssh_enabled = 'enabled',
        ssh_port = 22,
        http_enabled = 'disabled',
        http_port = 80,
        https_enabled = 'enabled',
        https_port = 443,

        log_enabled = 'disabled',
        # NOTE:
        # . currently, flexmaster don't accept this value of log_ip
        # . this is fm bug
        # . temporarily set dafault to disabled to avoid errror with ip 0.0.0.0
        log_port = 514,

        remote_mode = 'auto',
        fm_url = '', # NOTE: it can not be restored
        inform_interval = '1m', # this is not default but expected
    )


    def __init__(self, selenium_mgr, browser_type, ip_addr, config, https = True):
        """
        Input:
        - config: right now, the APWebUI get the parsed config from the RuckusAP class
        """
        self.config = config

        # init the father class
        WebUI.__init__(self, selenium_mgr, browser_type, ip_addr, https = https)

        self.HOME_PAGE = self.MAIN_PAGE # = 0
        self.HOME_PAGE_MENU = self.STATUS_DEVICE
        self._tmp_ = {} # temp storage
        self.CallHomeIntervalMin = 'Min'

        # defining values for "abstract" attributes
        try:
            self.username = config['username']
            self.password = config['password']
        except:
            pass

        self.info = self.resource['Locators']
        self.const = self.resource['Constants']
        self.s = self.selenium

        self.username_loc = self.info['LoginUsernameTxt']
        self.password_loc = self.info['LoginPasswordTxt']

        self.login_loc = self.info['LoginBtn']
        self.logout_loc = self.info['LogoutBtn']


    def _init_navigation_map(self):
        # AP has only one tab. So the homepage is chosen to be main tab
        self.MAIN_PAGE = self.info['MainPageLink']

        # STATUS menu
        self.STATUS_DEVICE = self.info['StatusDeviceLink']
        self.STATUS_INTERNET = self.info['StatusInternetLink']
        self.STATUS_WIRELESS = self.info['StatusWirelessLink']
        self.STATUS_LOCAL_SERVICES = self.info['StatusLocalServicesLink']

        # CONFIG menu
        self.CONFIG_DEVICE = self.info['ConfigDeviceLink']
        self.CONFIG_INTERNET = self.info['ConfigInternetLink']
        self.CONFIG_WIRELESS = self.info['ConfigWirelessLink']
        self.CONFIG_ACCESS_CONTROLS = self.info['ConfigAccessCtrlsLink']
        self.CONFIG_VLAN = self.info['ConfigVlanLink']

        # MAINTENANCE menu
        self.MAINTENANCE_UPGRADE = self.info['MtcUpgradeLink']
        self.MAINTENANCE_REBOOT_RESET = self.info['MtcRebootResetLink']
        self.MAINTENANCE_SUPPORT_INFO = self.info['MtcSupportInfoLink']

        # ADMIN menu
        self.ADMIN_MGMT = self.info['AdminMgmtLink']
        self.ADMIN_DIAGS = self.info['AdminDiagsLink']
        self.ADMIN_LOG = self.info['AdminLogLink']


    def init_temp_storage(self, **kwa):
        '''
        kwa:
        - timestamp
        '''
        if not self._tmp_.has_key(kwa['timestamp']):
            self._tmp_[kwa['timestamp']] = {}
        return self._tmp_[kwa['timestamp']]


    def _get_status(self, tab_index, menu_index, locator, is_navigate = True):
        self.login()
        if is_navigate == True:
            # Sometimes it takes quite long time to load this page especially
            # when change username/password so we increase timeout for
            self.navigate_to(tab_index, menu_index, timeout = 20)

        self.s.check_element_present(locator)
        return self.s.get_htable_content(locator)


    def get_device_status(self):
        # just try to wait a moment for the self.CONFIG_WIRELESS link present before go into it
        self.s.is_element_present(self.STATUS_DEVICE, 30)
        return self._get_status(self.MAIN_PAGE, self.STATUS_DEVICE, \
                               self.info['StatusDeviceTbl'])


    def get_internet_status(self):
        content = self._get_status(self.MAIN_PAGE, self.STATUS_INTERNET, \
                                  self.info['StatusInternetGeneralTbl'])

        content.update(self._get_status(self.MAIN_PAGE, self.STATUS_INTERNET, \
                                       self.info['StatusInternetConnTbl'], False))
        return content


    def get_wireless_common_status(self):
        return self._get_status(self.MAIN_PAGE, self.STATUS_WIRELESS, \
                               self.info['WirelessCommon_Tbl'])


    def get_wireless_status(self, index):
        """
        Output:
        - a list of 2 items: [general info table, connected devices table]
          the 'connected devices table' can be None, in case, there is no connected device
        """
        SW = 'StatusWireless_'
        WI = 'WirelessItem_'

        # locators
        WirelessItemTab = self.info[SW + 'ItemTabTmpl'] % index

        ItemTbl = self.info[WI + 'Tbl']
        IsDeviceConnected = self.info[WI + 'IsDeviceConnected']
        ConnectedDevicesTbl = self.info[WI + 'ConnectedDevicesTbl']

        # constants
        NoDeviceConnectedMsg = self.const['NoDeviceConnectedMsg']

        content = []

        #self.login()
        #self.navigate_to(self.MAIN_PAGE, self.STATUS_WIRELESS)

        self.s.click_and_wait(WirelessItemTab, .35) # go to wlan info page

        # get the general info of the wlan
        content.append(self.s.get_htable_content(ItemTbl))

        # get connected devices (if exists)
        msg = self.s.get_text()
        # if split-able then there is no connected device
        if len(msg.split(NoDeviceConnectedMsg)) < 2:
            device_tbl = []

            tbl_hdr = self.s.get_vtableHeader(ConnectedDevicesTbl)
            i = 1
            tbl_row = self.s.get_vtableRow(ConnectedDevicesTbl, i, tbl_hdr)
            while tbl_row != None:
                device_tbl.append(tbl_row)
                i += 1
                tbl_row = self.s.get_vtableRow(ConnectedDevicesTbl, i, tbl_hdr)

            content.append(device_tbl)
        else:
            content.append(None)
        return content


    def get_current_log(self):
        """
        Make sure you are logged in and navigated to Maintenance > Support Info page
        before using this function.
        """
        SI = 'SupportInfo_'
        # maintenance > support info page
        return self.s.get_text(self.info[SI + 'CurrentLog'])


    def set_call_home_interval(self, **kwa):
        '''
        TODO: update the case where interval is an integer
        kwa:
        - interval: can be a number or
                    one of these text: 1 minute, 5 minutes, 10 minutes... (not int)
        '''
        CallHomeIntCb = self.info['Management_CallHomeIntCb']
        SubmitBtn = self.info['Management_SubmitBtn']

        interval = kwa['interval'] if isinstance(kwa['interval'], int) \
                   else self.const['CallHomeInterval'][kwa['interval']]
        # Sometimes, it cannot see a combox to set call home interval so
        # increase timeout and check this element presented first
        self.navigate_to(self.MAIN_PAGE, self.ADMIN_MGMT, timeout = 20)
        self.s.is_element_present(CallHomeIntCb)
        self.s.select_option(CallHomeIntCb, interval)
        self.s.safe_click(SubmitBtn)
        self.s.wait_for_page_to_load()
        time.sleep(2) # for the change takes effect
        return int(interval.split(' ')[0]) # as int


    class _APResourceMap():
        def __init__(self, **kwargs):
            args = {}
            args.update(kwargs)

            self.info = args['locator'] if args.has_key('locator') else None
            self.const = args['constant'] if args.has_key('constant') else None

        def _map_device_general_items(self):

            p_node = 'DeviceGeneral_' # Provsioning > Configuration Templates

            self.ordered_items = ["device_name"]
            # Will define detail for locators later
            self.locs = {
                'device_name': '',
                'username'   : '',
                'password'   : '',
                'cpassword'   : '',
            }

        def _map_wlan_common_items(self):
            """
            This function is to map locator of WLAN Common items

            'WModeCb': "//select[@id='freqband']",
            'ChannelCb': "//select[@id='channel']",
            'ChannelWidthCb': "//select[@id='channelwidth']",
            'CountryCodeCb': "//select[@id='countrycode']",
            'CountryCodeCb': "//select[@id='countrycode']",
            # Item in Advance Setting
            'TxPowerCb': "//select[@id='txpower']",
            'ProtModeDisabledRd': "//input[@id='modeD']",
            'ProtModeCTSRd': "//input[@id='modeC']",
            'ProtModeCTSCTSRd': "//input[@id='modeRC']",
            'EditCommonBtn': "//input[@id='advancedsettings']",
            """
            p_node = 'WLANCommon_' # Provsioning > Configuration Templates

            self.ordered_items = ['wmode', 'channel', 'country_code', 'txpower', 'prot_mode']
            self.combobox_items = ['wmode', 'channel', 'country_code', 'txpower']
            #Special item
            self.multi_choice_items = ['prot_mode']
            # Extra items are items in 'Edit Common Setting' page
            self.extra_items = ['txpower', 'prot_mode']

            self.locs = {
                          #key: [checkbox locator, value locator]
                          'homepage'    : self.info[p_node + 'HomePage'],
                          'wmode'       : self.info[p_node + 'WModeCb'],
                          'channel'     : self.info[p_node + 'ChannelCb'],
                          'ChannelWidth': self.info[p_node + 'ChannelWidthCb'],
                          'country_code': self.info[p_node + 'CountryCodeCb'],
                          'txpower'     : self.info[p_node + 'TxPowerCb'],
                          # In this case, key is a value of prot_mode, will consider to let it a dictionary or a list.
                          'prot_mode'   : {
                                           'Disabled': self.info[p_node + 'ProtModeDisabledRd'],
                                           'CTS-only': self.info[p_node + 'ProtModeCTSRd'],
                                           'RTS-CTS': self.info[p_node + 'ProtModeRTSCTSRd']
                                          },
                          'edit_btn'    : self.info[p_node + 'EditCommonBtn'],
            }


        def _map_wlan_det_items(self):
            """
            This function is to map locator of WLAN detail items

            Note: Currently, we don't include "Key Entry Method" and "Beacon Interval" items.
            It is due to FM doesn't have these items.

            """
            p_node = 'WLANDet_' # Provsioning > Configuration Templates
            #List all items of WLAN Detail page in order
            self.ordered_items = [
                # Get info of items in the main page Wireless first
                'avail', 'broadcast_ssid', 'wlan_name', 'wlan_ssid', 'encrypt_method',
                'wep_mode', 'encryption_len', 'wep_key_idx', 'wep_passhrase', 'wep_pass', 'wpa_version',
                'wpa_algorithm', 'auth', 'psk_passphrase', 'radius_nas_id', 'auth_ip',
                'auth_port', 'auth_secret', 'acct_ip', 'acct_port', 'acct_secret',
                # Then get info of items in the extra pages: Threshold Setting and Rate Limiting
                # FM MR1 version: Removed 'frag_threshold' item
                'dtim', 'rtscts_threshold', 'downlink', 'uplink',
            ]

            self.combobox_items = ['downlink', 'uplink',
                                       'encrypt_method', 'encryption_len', 'wep_key_idx', ]
            self.multi_choice_items = ['avail', 'broadcast_ssid', 'client_isolation', 'rate_limiting',
                                       'wep_mode', 'wpa_version', 'wpa_algorithm', 'auth']
            # FM MR1 version: Removed 'frag_threshold' item
            self.textbox_items = ['wlan_name', 'wlan_ssid', 'dtim', 'rtscts_threshold',
                                       'radius_nas_id', 'wep_passhrase', 'wep_pass', 'psk_passphrase', 'auth_port', 'auth_secret',
                                       'acct_port', 'acct_secret', ]
            self.ip_items = ['auth_ip', 'acct_ip']

            # Here are items which have an addtitional locator for place of error message
            self.threshold_items = ['dtim', 'frag_threshold', 'rtscts_threshold']
            self.ratelimiting_items = ['downlink', 'uplink']


            self.locs = {   #There're two cases of loc_map
                          #1. 'normal item': input locator: combo box or txt box,
                          #2. 'multichoice item': List of choice like: 'Disabled': Disabled_loc, 'Enabled': 'Enabled_loc'}
                          'homepage': self.info[p_node + 'HomePageTmpl'],
                          'avail': {
                                    'Disabled': self.info[p_node + 'WAvailDRd'],
                                    'Enabled': self.info[p_node + 'WAvailERd']
                                   },
                          'broadcast_ssid': {
                                             'Disabled': self.info[p_node + 'WBroadcastDRd'],
                                             'Enabled': self.info[p_node + 'WBroadcastERd']
                                            },
                          # This option is not available on WebUI
                          #'client_isolation': {'Disabled': self.info[p_node + 'WIsolationDRd'],
                          #                     'Enabled': self.info[p_node + 'WIsolationERd']},
                          'wlan_name': self.info[p_node + 'WNameTxt'],
                          'wlan_ssid': self.info[p_node + 'WSSIDTxt'],

                          # Beacon interval, FM doesn't have this items
                          'beacon_int': self.info[p_node + 'WBeaConIntTxt'],
                          'dtim': self.info[p_node + 'WDTIMTxt'],
                          # FM MR1 version: Removed 'frag_threshold' item
                          #'frag_threshold'   : self.info[p_node + 'WFragThresTxt'], #Coi lai its locator
                          'rtscts_threshold' : self.info[p_node + 'WRTSCTSTxt'],
                          # Up/Down link for rate limiting
                          'downlink': self.info[p_node + 'WDownlinkCb'],
                          'uplink': self.info[p_node + 'WUplinkCb'],

                          'encrypt_method': self.info[p_node + 'WEncryptCb'],
                          #'Open, SharedKey, Auto',
                          'wep_mode': {
                                       'Open': self.info[p_node + 'WOpenRd'],
                                       'SharedKey': self.info[p_node + 'WSharedKeyRd'],
                                       'Auto': self.info[p_node + 'WAutoRd']
                                      },
                          'encryption_len': self.info[p_node + 'WEncryptLenCb'],
                          # Key Entry Method
                          'key_entry_method': {
                                               'hexa': self.info[p_node + 'WKeyEntryHexaRd'],
                                               'ascii': self.info[p_node + 'WKeyEntryAsciiRd']
                                              },
                          # Wireless 1 WEP Key Index
                          'wep_key_idx': self.info[p_node + 'WKeyIndexCb'],
                          # [Checkbox loc, passphrase, passphrase (confirm)]
                          'wep_passphrase': self.info[p_node + 'WWEPPassphraseTxt'],
                          # the wep_pass is the wep_key password
                          'wep_pass': self.info[p_node + 'WWEPKeyTxt'],
                          'generate_btn': self.info[p_node + 'WGenPassphraseBtn'],

                          #WPA Version
                          'wpa_version': {
                                          'WPA': self.info[p_node + 'WWPAVer1Rd'],
                                          'WPA2': self.info[p_node + 'WWPAVer2Rd'],
                                          'Auto': self.info[p_node + 'WWPAVerAutoRd']
                                         },
                          #Authentication: PSK, 802.1x, Auto
                          'auth': {
                                   'PSK': self.info[p_node + 'WAuthPSKRd'],
                                   '802.1x': self.info[p_node + 'WAuth802.1xRd'],
                                   'Auto': self.info[p_node + 'WAuthAutoRd']
                                  },

                          'psk_passphrase': self.info[p_node + 'WPSKPassphraseTxt'],
                          #WPA Algorithm: : TKIP, AES, Auto,
                          'wpa_algorithm': {
                                            'TKIP': self.info[p_node + 'WWPATKIPRd'],
                                            'AES': self.info[p_node + 'WWPAAESRd'],
                                            'Auto': self.info[p_node + 'WWPAAutoRd']
                                           },
                          # Passphrase for psk
                          'psk_passphrase' : self.info[p_node + 'WPSKPassphraseTxt'],
                          'radius_nas_id'  : self.info[p_node + 'WRadiusTxt'],

                          'auth_ip':  self.info[p_node + 'WAuthIPTxtTmpl'],
                          'auth_port': self.info[p_node + 'WAuthPortTxt'],
                          'auth_secret': self.info[p_node + 'WAuthSecretTxt'],
                          # FM UI has the confirm item for "authentication secret" but AP WebUI doesn't have it
                          'cauth_secret': self.info[p_node + 'WAuthSecretTxt'],

                          'acct_ip': self.info[p_node + 'WAcctIPTxtTmpl'],
                          'acct_port': self.info[p_node + 'WAcctPortTxt'],
                          #[Checkbox loc, server secret, server secret (confirm)]
                          'acct_secret': self.info[p_node + 'WAcctSecretTxt'],
                          # FM UI has the confirm item for "account secret" but AP WebUI doesn't have it
                          'cacct_secret': self.info[p_node + 'WAcctSecretTxt'],

                          # It is a link to go back after entering "Edit Threshold Setting", "Rate Limiting Setting" page
                          'threshold_btn': self.info[p_node + 'EditThresBtn'],
                          'ratelimiting_btn': self.info[p_node + 'EditRateLimitingBtn'],
                          'back_link': self.info[p_node + 'BackLinkLnk'],
                          'update_btn': "self.info[p_node + 'UpdateBtn']",
                      }


    def _get_value_from_multi_choice_items(self, **kwargs):
        """
        This function is to get value from items which have more than two radio button.
        It will return a "key" which its radio is ticked off.
        Note: Convention, the key is the value of radio button.
        """
        items = {}
        items.update(kwargs)

        v = False
        retries = 1

        # Some tiem the page load very slow, we need to sleep a moment then re-get it
        while True:
            try:
                for k, loc in items.iteritems():
                    self.s.check_element_present(loc)
                    v = self.s.is_checked(loc)
                    if v:
                        return k
            except Exception:
                logging.info('Cannot find locator of items: %s. Error: %s' % (items, traceback.format_exc()))

            # If go here, try to sleep for a moment then re-get again
            retries += 1
            if retries > 5: break

            logging.info('Cannot get value of items: %s' % items)
            logging.info('Sleep a moment and try %d times' % retries)
            time.sleep(10)

        raise Exception('Cannot get value of items: %s' % items)


    def _get_ip_items(self, locator):
        """
        This function is to four values from IP items which have four textboxes for each part of IP.
        It will return a completed IP which is a combination of the four values.
        Input:
        - locator: template locator or four IP parts. It looks like:
            "//input[@id='acct-ip0']": Locator for the first textbox
            "//input[@id='acct-ip1']": Locator for the second textbox
            "//input[@id='acct-ip2']": Locator for the third textbox
            "//input[@id='acct-ip3']": Locator for the fourth textbox

            => "//input[@id='acct-ip%d']": template locator
        """
        ip = ""

        for i in range(0, 4):
            self.s.check_element_present(locator % i)
            ip += self.s.get_value(locator % i).strip()
            if i <= 2:
                ip += "."

        return ip


    def get_device_items(self, **kwargs):
        '''
        This function is to get infomation of Device General from Configuration > Device.
        Current it is only get the Device name
        # TO DO:
        This function will be updated later
        '''

        ap_info = self.get_device_status()
        ret = {'device_name': "Device Name"}

        # compare the device names from both side
        ret['device_name'] = ap_info['Device Name']

        return ret


    def get_wlan_common_items(self, **kwargs):
        """
        This funtion is to get items of WLAN Common page. This function will return a dictionary.
        Keys of the dictionary will the same as its name from flexmaster > fillProWLANCommonItem.

        Because there are some items which we need to click Edit Setting button to get their status.
        Hence, the function will traverse items in order to save time.

        Input:
        - List of items which you want to get infomation. Below are items of WLAN Common:
            'wmode': 'auto, g, b',
            'channel': 'value from 0 to 11; 0: smartselect, 1: channel 1...',
            'country_code': 'AU, AT, ...',
            'txpower': 'max, half, quarter, eighth, min',
            'prot_mode': 'Disabled, CTS-only, RTS-CTS'

        We only can get txpower and prot_mode after clicking Edit Setting button

        The kwargs will follow below format:
            kwargs = {
                      'wmode': 'None/value', 'channel': 'None/value', 'country_code': 'None/value',
                      'txpower': 'None/value', 'prot_mode': 'None/value'
                     }
        """
        logging.info("--------Start: get_wlan_common_items--------")
        configured_items = {}
        configured_items.update(kwargs)

        if len(configured_items) <= 0:
            raise Exception('There is not any item to get for WLAN Detail')

        logging.info('Getting information for Wireless Common')

        extra_page = False
        ret = {}

        item_map = self._APResourceMap(constant = self.const, locator = self.info)
        item_map._map_wlan_common_items()

        # just try to wait a moment for the self.CONFIG_WIRELESS link present before go into it
        self.s.is_element_present(self.CONFIG_WIRELESS, 30)
        # Navigate to the Configuration WLAN Page first
        self.navigate_to(self.MAIN_PAGE, self.CONFIG_WIRELESS, force = True) # , timeout=15
        self.s.check_element_present(item_map.locs['homepage'])
        time.sleep(WLAN_PAGE_LOAD_WAIT)

        #Traverse all items in WLAN detail page and only configure items which are present in "conf"
        #Because the dictionary doesn't have order and there are some denpendent items,
        #they are shown only if their controls are selected.#Ex: sub-items of WEB, WPA, 802.1x, ...
        #Hence, with this way we will avoid a problem that the selenium doesn't see dependent items.
        for k in item_map.ordered_items:
            if not k in configured_items:
                continue

            # (k,v) = (item, configured_items[item])
            v = None
            if k in item_map.extra_items and not extra_page:
                self.s.click_and_wait(item_map.locs['edit_btn'])
                self.s.check_element_present(item_map.locs[k])
                time.sleep(WLAN_PAGE_LOAD_WAIT)
                extra_page = True

            #tick off the check box if it is not checked:
            if k in item_map.combobox_items:
                self.s.check_element_present(item_map.locs[k])
                v = self.s.get_selected_value(item_map.locs[k])

            elif k in item_map.multi_choice_items:
                v = self._get_value_from_multi_choice_items(**item_map.locs[k])

            elif k in item_map.textbox_items:
                self.s.check_element_present(item_map.locs[k])
                v = self.s.get_value(item_map.locs[k])

            ret[k] = v


        # map some items from a number to a value to make them the same as FM > Create Cfg Template
        txpower_map = {
            '0': 'max',
            '1': 'half',
            '2': 'quarter',
            '3': 'eighth',
            '4': 'min'
        }
        k = 'txpower'
        if ret.has_key(k):
            ret[k] = txpower_map[ret[k]]

        # map some items from a number to a value to make them the same as FM > Create Cfg Template
        # On AP fw 8.0, it already changed values to  auto, 11g so we don't map them
        #wmode_map = {
        #    'auto': 'auto',
        #    '11g': '11g',
        #    '11b': '11b',
        #    '11a': '11a',
        #}
        #k = 'wmode'
        #if ret.has_key(k):
        #    ret[k] = wmode_map[ret[k]]
        logging.info("--------Finish: get_wlan_common_items--------")
        return ret


    def get_wlan_det_items(self, **kwargs):
        """
        This funtion is to get items of WLAN Detail from 1 to 8 page. This function will return
        a dictionary. Keys of the dictionary will the same as its name from flexmaster > fillProWLANCommonItem.

        Because there are some items which we need to click Edit Setting button to get their status.
        Hence, the function will traverse items in order to save time.

        Input:
        - List of items which you want to get infomation. Below are items of WLAN Detail:
            {
                'wlan_num': 'The WLAN from 1 to 8 which you want to access',
                'avail': 'Disabled, Enabled',
                'broadcast_ssid': 'Disabled, Enabled',
                'client_isolation': 'Disabled, Enabled',
                'wlan_name': 'name of wlan',
                'wlan_ssid': 'name of ssid',
                'dtim': 'Data beacon rate (1-255)',
                # FM MR1 version: Removed 'frag_threshold' item
                #'frag_threshold': 'Fragment Threshold (245-2346',
                'rtscts_threshold': 'RTS / CTS Threshold (245-2346',
                'rate_limiting': 'Rate limiting: Disabled, Enabled',
                'downlink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
                'uplink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
                'encrypt_method': 'Diablded, WEB, WPA',

                'wep_mode': 'Open, SharedKey, Auto',
                'encryption_len': 'encryption length: 13, 26, 5, 10', #13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
                #Wireless 1 WEP Key Index
                'wep_key_idx': 'key index: 1, 2, 3, 4',
                #WEP key password
                'wep_pass': 'password of wep method',
                #'cwep_pass': ' password of wep method (confirm)',

                #WPA Version
                'wpa_version': 'WPA version: WPA, WPA2, Auto',
                #WPA Algorithm
                'wpa_algorithm': 'WPA Algorithm: TKIP, AES, Auto',
                #Authentication
                'auth': 'Authentication: PSK, 802.1x, Auto',
                'psk_passphrase': 'PSK passphrase',
                #'cpsk_passphrase': 'PSK passphrase (confirm)',
                'radius_nas_id': 'Radius NAS-ID',
                'auth_ip': 'Authentication IP address',
                'auth_port': 'Authentication Port',
                'auth_secret': 'Authentication Server Secret',
                'cauth_secret': 'Authentication Server Secret',
                'acct_ip': 'Accounting IP address',
                'acct_port': 'Accounting Port',
                'acct_secret': 'Accounting Server Secret',
                #'cacct_secret': 'Accounting Server Secret (confirm)'
            }

        The kwargs will follow below format:
            kwargs = {
                      list of items
                     }
        """
        logging.info("--------Start: get_wlan_det_items--------")
        configured_items = {}
        configured_items.update(kwargs)

        if len(configured_items) <= 0:
            raise Exception('There is not any item to get for WLAN Common')

        threshold_page = False
        ratelimiting_page = False

        ret = {'wlan_num': configured_items['wlan_num']}

        item_map = self._APResourceMap(constant = self.const, locator = self.info)
        item_map._map_wlan_det_items()

        # Get the wlan user want to get information
        # WLAN 1 -> index 0
        # WLAN 2 -> index 1...
        index = int(configured_items['wlan_num']) - 1
        logging.info('Getting information for Wireless %s' % configured_items['wlan_num'])

        # just try to wait a moment for the self.CONFIG_WIRELESS link present before go into it
        self.s.is_element_present(self.CONFIG_WIRELESS, 30)
        # Navigate to the Configuration WLAN Page first
        self.navigate_to(self.MAIN_PAGE, self.CONFIG_WIRELESS, force = True) # timeout=15,

        self.s.check_element_present(item_map.locs['homepage'] % index)
        time.sleep(WLAN_PAGE_LOAD_WAIT)
        # Then go to the wirelss tab which user wants to get info
        self.s.click_and_wait(item_map.locs['homepage'] % index)
        time.sleep(WLAN_PAGE_LOAD_WAIT)

        #Traverse all items in WLAN detail page and only configure items which are present in "conf"
        #Because the dictionary doesn't have order and there are some denpendent items,
        #they are shown only if their controls are selected.#Ex: sub-items of WEB, WPA, 802.1x, ...
        #Hence, with this way we will avoid a problem that the selenium doesn't see dependent items.
        for k in item_map.ordered_items:
            if not k in configured_items:
                continue

            v = None
            # We have an issue here. Sometime the page loaded very slow and some function cannot
            # get their value. Temporarily, we re-try to get value for 3 times if v == None
            if k in item_map.threshold_items and not threshold_page:
                self.s.click_and_wait(item_map.locs['threshold_btn'], 2)
                self.s.check_element_present(item_map.locs[k])
                time.sleep(WLAN_PAGE_LOAD_WAIT)

                threshold_page = True
            elif k in item_map.ratelimiting_items and not ratelimiting_page:
                # Because current page is "Edit Threshold page" when enter this page
                # so we need to click "Go back to Wireless Configuration" to back to the main page of WLAN first
                self.s.click_and_wait(item_map.locs['back_link'], 2)
                self.s.check_element_present(item_map.locs['homepage'] % index)
                time.sleep(WLAN_PAGE_LOAD_WAIT)
                # Then click Edit Rate Limiting button to enter its page.
                self.s.click_and_wait(item_map.locs['ratelimiting_btn'], 2)
                self.s.check_element_present(item_map.locs[k])
                time.sleep(WLAN_PAGE_LOAD_WAIT)
                ratelimiting_page = True

            if k in item_map.combobox_items:
                self.s.check_element_present(item_map.locs[k])
                v = self.s.get_selected_value(item_map.locs[k])

            elif k in item_map.multi_choice_items:
                v = self._get_value_from_multi_choice_items(**item_map.locs[k])

            elif k in item_map.textbox_items:
                self.s.check_element_present(item_map.locs[k])
                v = self.s.get_value(item_map.locs[k])

            elif k in item_map.ip_items:
                v = self._get_ip_items(item_map.locs[k])

            ret[k] = v

            # after go out of the loop while, if the v is still None raise exception
            if v == None:
                raise Exception('Cannot get value for the item %s' % item_map.locs[k])

        # if their value is '0' (Disabled), it means Rate Limiting is disabled so remove uplink/downlink .
        # And when rate limiting is "Disabled", uplink/downlink will not be provided
        # May be, don't need this code for uplink/downlink. Check later
        #if (ret.has_key('uplink') or ret.has_key('downlink')) and\
        #    (ret['uplink'] == 0 or ret['downlink'] == 0):
        #    ret.pop('uplink')
        #    ret.pop('downlink')

        # map some items from a number to a value to make them the same as FM > Create Cfg Template
        encryption_map = {
            '0': 'Disabled',
            'wep': 'WEP',
            'wpa': 'WPA',
        }
        k = 'encrypt_method'
        if ret.has_key(k):
            ret[k] = encryption_map[ret[k]]

        # Because values for Encryption Strenght combobox on AP WebUI  are differnent from FM,
        # so we need to re-calculate it before return the result
        # The values on FM: 13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
        # The valuee on AP: 5 and 13. We need to base on "Key Entry Method" to calculate it.
        # Below are value from combinations of "Encryption Strenght" and "Key Entry Method".
        #   value = 5: if len = 5 and mode=ascii => 64bit 5 ascii
        #   value = 10: if len = 5 and mode=hex => 64bit 10 hex
        #   value = 13: if len = 13 and mode=ascii => 128bit 13 ascii
        #   value = 26: if len = 13 and mode=hex => 128bit 26 hex
        if configured_items.has_key('encryption_len'):
            # If the back link is present, it means it is being in either "Edit Threshold" or "Rate Limiting"
            # Click the "back link" to go back to the main wlan page before getting key_entry_mode
            if (self.s.is_element_present(item_map.locs['back_link'])):
                self.s.click_and_wait(item_map.locs['back_link'])
                self.s.check_element_present(item_map.locs['homepage'] % index)
                time.sleep(WLAN_PAGE_LOAD_WAIT)

            mode = self._get_value_from_multi_choice_items(**item_map.locs['key_entry_method'])
            map_len = {
                '5':   '5' if 'ascii' == mode else '10',
                '13': '13' if 'ascii' == mode else '26',
            }
            ret['encryption_len'] = map_len[ret['encryption_len']]

        logging.info("--------Finish: get_wlan_det_items--------")
        return ret


    def get_internet_items(self):
        """
        This funtion is to get items of WLAN Common page. This function will return a dictionary.
        Keys of the dictionary will the same as its name from flexmaster > fillProInternetItem.
        """
        pass

    def set_fm_url(self, **kwa):
        '''
        NOTE: make sure you set Call Home interval to min before calling this
        - Set FM URL to the given one
        - Refresh the page and wait for successfully contacted
        kwa:
        - url: the flexmaster url
        - validate_url: validate whether AP can use this url to contact FM successfully.
                        Default is 'True' for back compatibility
        '''
        _kwa = {
            'url':'',
            'validate_url': True,
        }
        _kwa.update(kwa)

        FmUrlTxt = self.info['Management_FmUrlTxt']
        SubmitBtn = self.info['Management_SubmitBtn']
        Tr069StatusTbl = self.info['Management_Tr069StatusTbl']

        logging.info('Set AP FM URL to "%s"' % _kwa['url'])
        self.navigate_to(self.MAIN_PAGE, self.ADMIN_MGMT, 2)
        if not self.s.is_element_present(FmUrlTxt, 30): raise Exception('Not found element %s to set FM URL' % FmUrlTxt)
        self.s.type_text(FmUrlTxt, _kwa['url'])
        self.s.safe_click(SubmitBtn)
        self.s.wait_for_page_to_load()

        if _kwa['validate_url']:
            endtime = time.time() + 300 # = 5 mins
            tbl = self.s.get_htable_content(Tr069StatusTbl)
            status = tbl[find_key(keys = tbl.keys(), match = 'Last successful contact')]
            logging.info('Wait for the status to be changed')
            #logging.debug('Current status: %s' % status)
            while time.time() < endtime:
                if _kwa['url'].lower() in status.lower(): return
                time.sleep(2)
                self.navigate_to(self.MAIN_PAGE, self.ADMIN_MGMT, force = True)
                if not self.s.is_element_present(Tr069StatusTbl, 30): break # wait for page 2 load
                tbl = self.s.get_htable_content(Tr069StatusTbl)
                status = tbl[find_key(keys = tbl.keys(), match = 'Last successful contact')]
            raise Exception('Failed to set FM URL for %s' % self.ip_addr)


    def set_mgmt_type(self, **kwa):
        '''
        - Set the TR069/SNMP Management Choice
        kwa:
        - type: one of auto, snmp, flexmaster
        '''
        SelectedType = {
            'auto': self.info['Management_AutoRadio'],
            'snmp': self.info['Management_SnmpRadio'],
        }[kwa['type']]

        SubmitBtn = self.info['Management_SubmitBtn']
        logging.info('Set AP management type to %s' % kwa['type'])
        self.navigate_to(self.MAIN_PAGE, self.ADMIN_MGMT)
        self.s.click_and_wait(SelectedType, .5)
        self.s.safe_click(SubmitBtn)
        self.s.wait_for_page_to_load()
        time.sleep(2) # for change takes effect


    def get_version(self):
        '''
        . not yet implemented
        '''
        return None
