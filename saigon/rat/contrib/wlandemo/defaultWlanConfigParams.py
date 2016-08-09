import random
from RuckusAutoTest.common.Ratutils import make_random_string

DEFAULT_wlan_config_params = {}
DEFAULT_wlan_config_params['open-none'] = {
    'ssid': 'open-none',
    'auth': 'open',
    'wpa_ver': '',
    'encryption': 'none',
    'sta_auth': 'open',
    'sta_encryption': 'none',
    'sta_wpa_ver': '',
    'key_index': '',
    'key_string': '',
    'ad_domain': '',
    'ad_addr': '',
    'ad_port': '',
    'ras_addr': '',
    'ras_port': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': ''
}

DEFAULT_wlan_config_params['open-wep64'] = {
    'ssid': 'open-wep64-local',
    'auth': 'open',
    'encryption': 'WEP-64',
    'wpa_ver': '',
    # 'key_index': '1', 'key_string': 'f12a982cb1dec862b6795b1ac3',
    'key_index': "1", 'key_string': make_random_string(10, "hex"),
    'sta_auth': 'open',
    'sta_encryption': 'WEP-64',
    'sta_wpa_ver': '',
    'ad_domain': '',
    'ad_port': '',
    'ad_addr': '',
    'ras_addr': '',
    'ras_port': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': ''
}

DEFAULT_wlan_config_params['open-wep128'] = {
    'ssid': 'open-wep128',
    'auth': 'open',
    'encryption': 'WEP-128',
    'wpa_ver': '',
    # 'key_index': '1', 'key_string': 'f12a982cb1dec862b6795b1ac3',
    'key_index': "1" , 'key_string': make_random_string(26, "hex"),
    'sta_auth': 'open',
    'sta_encryption': 'WEP-128',
    'sta_wpa_ver': '',
    'ad_domain': '',
    'ad_port': '',
    'ad_addr': '',
    'ras_addr': '',
    'ras_port': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': ''
}


DEFAULT_wlan_config_params['share-wep64'] = {
    'ssid': 'share-wep64',
    'auth': 'shared',
    'encryption': 'WEP-64',
    'wpa_ver': '',
    # 'key_index': '1', 'key_string': 'f12a982cb1dec862b6795b1ac3',
    'key_index': "1" , 'key_string': make_random_string(10, "hex"),
    'sta_auth': 'shared',
    'sta_encryption': 'WEP-64',
    'sta_wpa_ver': '',
    'ad_domain': '',
    'ad_port': '',
    'ad_addr': '',
    'ras_addr': '',
    'ras_port': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': ''
}

DEFAULT_wlan_config_params['share-wep128'] = {
    'ssid': 'share-wep128',
    'auth': 'shared',
    'encryption': 'WEP-128',
    'wpa_ver': '',
    # 'key_index': '1', 'key_string': 'f12a982cb1dec862b6795b1ac3',
    'key_index': "1", 'key_string': make_random_string(26, "hex"),
    'sta_auth': 'shared',
    'sta_encryption': 'WEP-128',
    'sta_wpa_ver': '',
    'ad_domain': '',
    'ad_port': '',
    'ad_addr': '',
    'ras_addr': '',
    'ras_port': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': ''
}

DEFAULT_wlan_config_params['psk-wpa-tkip'] = {
    'ssid': 'psk-wpa-tkip-local',
    'auth': 'PSK',
    'encryption': 'TKIP',
    'wpa_ver': 'WPA',
    # 'key_index': '', 'key_string': '031cdff423e150a6408bb2e11a7b331868b01252d812a',
    'key_index': "", 'key_string': make_random_string(random.randint(8, 63), "hex"),
    'sta_auth': 'PSK',
    'sta_encryption': 'TKIP',
    'sta_wpa_ver': 'WPA',
    'ras_port': '',
    'ad_domain': '',
    'ad_addr': '',
    'ad_port': '',
    'ras_addr': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': '',
}

DEFAULT_wlan_config_params['psk-wpa-aes'] = {
    'ssid': 'psk-wpa-aes-local',
    'auth': 'PSK',
    'encryption': 'AES',
    'wpa_ver': 'WPA',
    # 'key_index': '', 'key_string': '77a2c471dff2a77a6e30720cad40ef1482b07965797c7b1d6763c',
    'key_index': "" , 'key_string': make_random_string(random.randint(8, 63), "hex"),
    'sta_auth': 'PSK',
    'sta_encryption': 'AES',
    'sta_wpa_ver': 'WPA',
    'ras_port': '',
    'ad_domain': '',
    'ad_addr': '',
    'ad_port': '',
    'ras_addr': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': '',
}


DEFAULT_wlan_config_params['psk-wpa2-tkip'] = {
    'ssid': 'psk-wpa2-tkip-local',
    'auth': 'PSK',
    'encryption': 'TKIP',
    'wpa_ver': 'WPA2',
    # 'key_index': '', 'key_string': '893b98db056a7d9da41',
    'key_index': "", 'key_string': make_random_string(random.randint(8, 63), "hex"),
    'sta_auth': 'PSK',
    'sta_encryption': 'TKIP',
    'sta_wpa_ver': 'WPA2',
    'ras_port': '',
    'ad_domain': '',
    'ad_addr': '',
    'ad_port': '',
    'ras_addr': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': '',
}

DEFAULT_wlan_config_params['psk-wpa2-aes'] = {
    'ssid': 'psk-wpa2-aes-local',
    'auth': 'PSK',
    'encryption': 'AES',
    'wpa_ver': 'WPA2',
    'key_index': "" , 'key_string': make_random_string(random.randint(8, 63), "hex"),
    'sta_auth': 'PSK',
    'sta_encryption': 'AES',
    'sta_wpa_ver': 'WPA2',
    'ras_port': '',
    'ad_domain': '',
    'ad_addr': '',
    'ad_port': '',
    'ras_addr': '',
    'username': 'ras.local.user',
    'password': 'ras.local.user',
    'ras_secret': '',
}

DEFAULT_wlan_config_params['eap-wpa-aes'] = {
    'ssid': 'eap-wpa-aes-ras',
    'auth': 'EAP',
    'encryption': 'AES',
    'wpa_ver': 'WPA',
    'key_string': '',
    'key_index': '',
    'sta_wpa_ver': 'WPA',
    'sta_auth': 'EAP',
    'sta_encryption': 'AES',
    'use_radius': True,
    'ras_addr': '192.168.0.252',
    'ras_port': '1812',
    'ras_secret': '1234567890',
    'username': 'ras.eap.user',
    'password': 'ras.eap.user',
}

DEFAULT_wlan_config_params['eap-wpa-tkip'] = {
    'ssid': 'eap-wpa-tkip-ras',
    'auth': 'EAP',
    'encryption': 'TKIP',
    'wpa_ver': 'WPA',
    'key_string': '',
    'key_index': '',
    'sta_auth': 'EAP',
    'sta_encryption': 'TKIP',
    'sta_wpa_ver': 'WPA',
    'use_radius': True,
    'ras_addr': '192.168.0.252',
    'ras_port': '1812',
    'ras_secret': '1234567890',
    'username': 'ras.eap.user',
    'password': 'ras.eap.user',
}

DEFAULT_wlan_config_params['eap-wpa2-aes'] = {
    'ssid': 'eap-wpa2-aes-ras',
    'auth': 'EAP',
    'encryption': 'AES',
    'wpa_ver': 'WPA2',
    'key_string': '',
    'key_index': '',
    'sta_wpa_ver': 'WPA2',
    'sta_auth': 'EAP',
    'sta_encryption': 'AES',
    'use_radius': True,
    'ras_addr': '192.168.0.252',
    'ras_port': '1812',
    'ras_secret': '1234567890',
    'username': 'ras.eap.user',
    'password': 'ras.eap.user',
}

DEFAULT_wlan_config_params['eap-wpa2-tkip'] = {
    'ssid': 'eap-wpa2-tkip-ras',
    'auth': 'EAP',
    'encryption': 'TKIP',
    'wpa_ver': 'WPA2',
    'key_string': '',
    'key_index': '',
    'sta_auth': 'EAP',
    'sta_encryption': 'TKIP',
    'sta_wpa_ver': 'WPA2',
    'use_radius': True,
    'ras_addr': '192.168.0.252',
    'ras_port': '1812',
    'ras_secret': '1234567890',
    'username': 'ras.eap.user',
    'password': 'ras.eap.user',
}

def get_cfg_list():
    return DEFAULT_wlan_config_params

def get_cfg_keys():
    return DEFAULT_wlan_config_params.keys()

def get_cfg(ckey):
    return DEFAULT_wlan_config_params[ckey]

