import sys

sys.path += ['../../RatToolAgent']

import RatToolAgent as rta

wlan =  {'username': 'ras.ul.526.dl.751kbps', 'ssid': 'eap-rate-limit', 'encrypt_method': 'TKIP', 'key_material': '', 'key_type': '', 'use_onex': True, 'password': 'ras.ul.526.dl.751kbps', 'auth_method': 'WPA'}
ssid = wlan.pop('ssid')
auth_method = wlan.pop('auth_method')
encrypt_method = wlan.pop('encrypt_method')
rta.set_wlan_profile(ssid, auth_method, encrypt_method, **wlan)

