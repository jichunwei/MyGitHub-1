# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
Abstract base class which models an 802.11 non-AP station (aka client) testbed component.
"""

from RuckusAutoTest.models import ComponentBase, TestbedComponent

class Station(ComponentBase):
    """
    Abstract base class which models an 802.11 non-AP station (aka client) testbed component.
    """

    def __init__(self, component_info, config):
        ComponentBase.__init__(self, component_info, config)

    def get_ip_addr(self):
        """ Return the Ip address of station."""
        pass

    def remove_all_wlan(self):
        """
        Remove all SSIDs from windows prefered wireless network list.
        """
        pass

    def verify_component(self):
        # Perform sanity check on the component: bare minimum check to
        # make sure test engine can access the component
        # Subclass must implement this function
        raise Exception ("DUT subclass didn't implement verify_component")

    def cfg_wlan(self, wlan_conf):
        """
        Configure the station to associate with the specified SSID
        using the supplied security parameters.
        The security parameters are the same that wpstool expects.
        All other prefered networks will be removed to ensure this is the
        only SSID with which the PC will associate.
        Input:
        wlan_conf: a dictionary that holds all the security setting for configuring a wireless profile on the station.
        """
        pass

    def ping(self, target_ip):
        """
        Execute a ping from the local host to the target IP address
        """
        pass

    def get_current_status(self):
        """
        Obtain current status of the wireless adapter on the local system
        """
        pass

    def convert_to_wlan_profile_syntax(self, wlan_conf):
        """
        Make the security parameters conform with WlanProfile schema syntax
        This function is useful to the derived classes StationWinPC and RemoteStationWinPC
        Input:
        wlan_conf: a dictionary that holds all the security setting for configuring a wireless profile on the station. Currently the components cares
        the following keys only:
        - wlan_conf['ssid']: a string represents the SSID of the WLAN
        - wlan_conf['auth']: authentication method, can be "open", "shared", "PSK", or "EAP"
        - wlan_conf['wpa_ver']: WPA version, can be "WPA" or "WPA2"
        - wlan_conf['encryption']: encryption method, can be "WEP64", "WEB128", "TKIP" or "AES"
        - wlan_conf['key_string']: key material, can be a string of ASCII characters or string of hexadecimal characters
        - wlan_conf['key_index']: WEP key index, can be 1, 2, 3 or 4
        - wlan_conf['username'] and wlan_conf['password']: user credentials
        Output: a dictionary that holds all the keys that the WlanTool module needs
        """
        conf = {'name': None, 'ssid': None, 'description': None, 'auth': None, 'wpa_ver': None, 'encryption': None,
                'key_string': None, 'key_index': None, 'username': None, 'password': None}
        conf.update(wlan_conf)
        param = dict()

        if conf['name'] is not None: 
            param['ssid'] = wlan_conf['name']
        elif conf['ssid'] is not None:
            param['ssid'] = wlan_conf['ssid']
        else:
            raise Exception("the dict is not included the ssid value about the wlan config.")
        
        param['use_onex'] = False
        if conf['auth'] == 'PSK':
            if conf['wpa_ver'] == 'WPA':
                param['auth_method'] = 'WPAPSK'
            elif conf['wpa_ver'] == 'WPA2':
                param['auth_method'] = 'WPA2PSK'
        elif conf['auth'] == 'EAP':
            if conf['wpa_ver'] == 'WPA' or conf['wpa_ver'] == 'WPA2':
                param['auth_method'] = conf['wpa_ver']
            else:
            #Cherry updated: For eap, encryption can be null in 9.2.
            #elif conf['encryption'] is not None and conf['encryption'].startswith('WEP'):
                param['auth_method'] = "open"
            param['use_onex'] = True
        elif conf['auth'].lower() == 'mac' or conf['auth'].lower() == 'maceap':
            if conf['wpa_ver'] == 'WPA':
                param['auth_method'] = 'WPAPSK'
            elif conf['wpa_ver'] == 'WPA2':
                param['auth_method'] = 'WPA2PSK'
            else:
                param['auth_method'] = "open"
        elif conf['auth'] is not None:
            param['auth_method'] = conf['auth']

        if conf['encryption'] is not None:
            if conf['encryption'].startswith('WEP'):
                param['encrypt_method'] = 'WEP'
            #Chico, 2015-5-22, add WPA2/Auto handling
            elif conf['encryption'].lower() == 'auto':
                import random
                encrypt_option_list=['TKIP','AES']
                param['encrypt_method']=encrypt_option_list[random.randrange(len(encrypt_option_list))]
            #Chico, 2015-5-22, add WPA2/Auto handling
            else:
                param['encrypt_method'] = conf['encryption']

        if conf['key_string'] is not None: param['key_material'] = conf['key_string']
        else:
            param['key_material'] = ''
            

        if conf['encryption'] is not None:
            if param['encrypt_method'] == 'WEP':
                param['key_type'] = 'networkKey'
            elif param['encrypt_method'] == 'TKIP' or param['encrypt_method'] == 'AES':
                # The key is a hexadecimal string
                if len(param['key_material']) == 64:
                    param['key_type'] = 'networkKey'
                # The key is obtained automatically
                elif len(param['key_material']) == 0:
                    param['key_type'] = ''
                # The key is an ASCII string
                else:
                    param['key_type'] = 'passPhrase'

        if conf['key_index'] is not None: param['key_index'] = conf['key_index']
        if conf['username'] is not None: param['username'] = conf['username']
        if conf['password'] is not None: param['password'] = conf['password']

        return param
