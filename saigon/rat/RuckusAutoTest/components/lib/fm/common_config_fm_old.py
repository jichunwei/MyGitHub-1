from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *


def get_wlan_cfg(domain = 'client', cfg = {}):
    '''
    input:
    . cfg: ssid should be input, suggested get it from get_unique_name()
           cfg is followed fmCfg format
    . domain: one of 'client', 'fm'
    '''
    _cfg = dict(
       wlan_ssid = '_ruckus_',
       avail = 'enabled',
       broadcast_ssid = 'enabled',
       encrypt_method = 'wpa',
       wpa_algorithm = 'tkip',
       wpa_version = 'wpa',
       auth = 'psk',
       psk_passphrase = 'lab4man1',
    )
    _cfg.update(cfg)
    if domain.lower() == 'fm':
        return _cfg
    return map_station_cfg(_cfg)

