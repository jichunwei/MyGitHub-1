import copy
import re


CfgValueMap = {
    # Device View > Details > Wireless Common
    'wmode': {
        'auto': '.*([aA]uto|AUTO).*', # AUTO
        '11g': '.*802.11[gG].*', # 802.11g
        '11ng': '.*802.11([bB].*[gG].*[nN]|[nN][gG]).*', # 7942
    },
    'channel': {
        '0': '.*[Ss]mart.*[Ss]elect.*',
        '1': '.*[Cc]hannel.*1.*',
        '2': '.*[Cc]hannel.*2.*',
        '3': '.*[Cc]hannel.*3.*',
        '4': '.*[Cc]hannel.*4.*',
        '5': '.*[Cc]hannel.*5.*',
        '6': '.*[Cc]hannel.*6.*',
        '7': '.*[Cc]hannel.*7.*',
        '8': '.*[Cc]hannel.*8.*',
        '9': '.*[Cc]hannel.*9.*',
        '10': '.*[Cc]hannel.*10.*',
        '11': '.*[Cc]hannel.*11.*',
    },
    'channel_width': {
        '20': '.*20.*[Mm][Hh][Zz].*',
        '40': '.*40.*[Mm][Hh][Zz].*',
    },
    'channel_width_1': {
        '20': '.*20.*[Mm][Hh][Zz].*',
        '40': '.*40.*[Mm][Hh][Zz].*',
    },
    'channel_width_2': {
        '20': '.*20.*[Mm][Hh][Zz].*',
        '40': '.*40.*[Mm][Hh][Zz].*',
    },
    'txpower': {
        'max'    : '.*([Ff]ull|[Mm]ax).*', #Full
        'half'   : '.*[Hh]alf.*-3.*[dD][Bb].*', # Half(-3 dB)
        'quarter': '.*[Qq]uarter.*-6.*[dD][Bb].*', #Quarter(-6dB)
        'eighth' : '.*[Ee]ighth.*-9.*[dD][Bb].*', #Eighth(-9 dB)
        'min'    : '.*([Mm]inimum|[Mm]in).*', # Minimum
    },
    'country_code' : {
        'AT': 'Austria',
        'CA': 'Canada',
        'CN': 'China',
        'FR': 'France',
        'ID': 'Indonesia',
        'JP': 'Japan',
        'TW': 'Taiwan',
        'CH': 'Switzerland',
        'SE': 'Sweden',
        'GB': 'United Kingdom',
        'US': 'United States',

    },
    # Device View > Details > Wireless Common
    'encryption_len': {
        '5' : '.*64.*[bB]it.*5.*([aA]scii|ASCII).*', # 64bit 5 ascii keys
        '10': '.*64.*[bB]it.*10.*([hH]ex|HEX).*', # 64bit 10hex digits
        '13': '.*128.*[bB]it.*13.*([aA]scii|ASCII).*', # 128bit 13 ascii keys
        '26': '.*128.*[bB]it.*26.*([hH]ex|HEX).*', # 128bit 26 hex digits
    },
    'wep_key_idx': {
        '1': '.*1.*', # 1
        '2': '.*2.*', # 2
        '3': '.*3.*', # 3
        '4': '.*4.*', # 4
    },


    # Device View > Details > Device
    'monitoring_mode': dict(
        disabled= 'Disable',
        active=   'Active',
        passive=  'Passive',
    ),
    'monitoring_interval_unit': dict(
        second= 'second\(s\)',
        minute= 'minute\(s\)',
    ),

    # Rate limiting items. This map will work for both of FM Provisioning,
    # FM Device View, and AP web UI
    'uplink': {
        'disabled': '.*[dD]isabled.*',
        '100kbps' : '.*100.*[kK][bB]ps.*',
        '250kbps' : '.*250.*[kK][bB]ps.*',
        '500kbps' : '.*500.*[kK][bB]ps.*',
        '1mbps'   : '.*1( |)[mM][bB]ps.*', # FM Provisioning: "1 mbps"; FMDV: "1mbps"; AP: "1 mbps link per second"
        '2mbps'   : '.*2( |)[mM][bB]ps.*', # FM Provisioning: "2 mbps"; FMDV: "2mbps"; AP: 2 mbps link per second
        '5mbps'   : '.*5( |)[mM][bB]ps.*', # FM Provisioning: 5 mbps; FMDV: 5mbps; AP: 5 mbps link per second
        '10mbps'  : '.*10( |)[mM][bB]ps.*', # FM Provisioning: 10 mbps; FMDV: 10mbps; AP: 10 mbps link per second
        '20mbps'  : '.*20( |)[mM][bB]ps.*', # FM Provisioning: 20 mbps; FMDV: 20mbps; AP: 20 mbps link per second
        '50mbps'  : '.*50( |)[mM][bB]ps.*', # FM Provisioning: 50 mbps; FMDV: 50mbps; AP: 50 mbps link per second
    },
    'downlink': {
        'disabled': '.*[dD]isabled.*',
        '100kbps' : '.*100.*[kK][bB]ps.*',
        '250kbps' : '.*250.*[kK][bB]ps.*',
        '500kbps' : '.*500.*[kK][bB]ps.*',
        '1mbps'   : '.*1( |)[mM][bB]ps.*', # FM Provisioning: "1 mbps"; FMDV: "1mbps"; AP: "1 mbps link per second"
        '2mbps'   : '.*2( |)[mM][bB]ps.*', # FM Provisioning: "2 mbps"; FMDV: "2mbps"; AP: 2 mbps link per second
        '5mbps'   : '.*5( |)[mM][bB]ps.*', # FM Provisioning: 5 mbps; FMDV: 5mbps; AP: 5 mbps link per second
        '10mbps'  : '.*10( |)[mM][bB]ps.*', # FM Provisioning: 10 mbps; FMDV: 10mbps; AP: 10 mbps link per second
        '20mbps'  : '.*20( |)[mM][bB]ps.*', # FM Provisioning: 20 mbps; FMDV: 20mbps; AP: 20 mbps link per second
        '50mbps'  : '.*50( |)[mM][bB]ps.*', # FM Provisioning: 50 mbps; FMDV: 50mbps; AP: 50 mbps link per second
    },
    'inform_interval': {
        # minute interval unit
        '1m': '1( |)[mM]inute(|[sS])',
        '5ms': '5( |)[mM]inute([sS]|)',
        '10ms': '10( |)[mM]inute([sS]|)',
        '15ms': '15( |)[mM]inute([sS]|)',
        '30ms': '30( |)[mM]inute([sS]|)',
        '30ms': '30( |)[mM]inute([sS]|)',
        # hour interval unit
        '1h': '1( |)[Hh]our(|[sS])',
        '4hs': '4( |)[Hh]our([sS]|)',
        '12hs': '12( |)[Hh]our([sS]|)',
        '24hs': '24( |)[Hh]our([sS]|)',
        # week interval unit
        '1w': '1( |)[Ww]eek(|[sS])',
        '2ws': '2( |)[Ww]eek([sS]|)',
        '4ws': '4( |)[Ww]eek([sS]|)',

    },
}
# Add map values for dual band AP like 7962
MIN_CHANNELS_RD_MODE_1 = 1
MAX_CHANNELS_RD_MODE_1 = 11
MIN_CHANNELS_RD_MODE_2 = 36
MAX_CHANNELS_RD_MODE_2 = 165
channel_1 = {'0': '.*[Ss]mart.*[Ss]elect.*',}
for i in range(MIN_CHANNELS_RD_MODE_1, MAX_CHANNELS_RD_MODE_1+1):
    channel_1['%s' % i] = '.*[Cc]hannel.*%s.*' % i

for i in range(MIN_CHANNELS_RD_MODE_2, MAX_CHANNELS_RD_MODE_2+1):
    channel_1['%s' % i] = '.*[Cc]hannel.*%s.*' % i

channel_2 = copy.deepcopy(channel_1)
CfgValueMap['channel_1'] = channel_1
CfgValueMap['channel_2'] = channel_2


def map_cfg_value(cfg, toSelect=True):
    '''
    . Map the input values to combo box selectable-options
    input:
    . cfg: the config for mapping
    . toSelect: to Select of webUI or from WebUI to value
    '''
    # Create a copy of passed param "cfg" to avoid changing its original values
    map_cfg = copy.deepcopy(cfg)
    for k in cfg.iterkeys():
        if not CfgValueMap.has_key(k): continue
        if toSelect:
            map_cfg[k] = CfgValueMap[k][map_cfg[k]]
        else:
            isFound = False
            for cvK, cvI in CfgValueMap[k].iteritems():
                m = re.match(cvI, map_cfg[k])
                if m:
                    map_cfg[k] = cvK
                    isFound = True
                    break
            if not isFound:
                raise Exception('Value mapping is not defined for %s', cfg[k])
    return map_cfg


def map_station_cfg(fm_cfg):
    '''
    This function is to map fm config to station config. Because fm config
    is not consistent with the station cfg which is built long time ago.

    1. Keys and values of station config:
        ssid = '',           #<--> wlan_ssid
        encryption = "WEP64", "WEB128", "TKIP" or "AES",      #<--> encryption_len/wpa_algorithm
        auth = "open", "shared", "PSK" or "EAP" = '802.1x',  #<--> wep_mode/auth
        wpa_ver = "WPA" or "WPA2",    #<--> wpa_version
        key_string = '',     #<--> wep_pass
        key_index = '',      #<--> wep_key_idx

        username = '',
        password = '',

    2. Keys and values of fm config:
        encrypt_method = 'WEP', 'WPA'

        wlan_ssid
        auth = 'open', 'sharedkey', 'auto', 'psk', 'eap' = '802.1x'
        wpa_version = 'wpa', 'wpa2'

        encryption_len = '5', '10', '13', '26'
        wpa_algorithm = 'tkip', 'aes'

        wep_pass
        wep_key_idx
        # username/password of Radius server for eap authentication
        username = '',
        password = '',

    3. Map between station and fm cfg key
            Station                 FM
            ssid            <--> wlan_ssid
            encryption  <--> encryption_len/wpa_algorithm
            auth        <--> wep_mode/auth
            wpa_ver     <--> wpa_version
            key_string      <--> wep_pass, psk_passphrase
            key_index       <--> wep_key_idx

            username        <--> useraname
            password        <--> password

    Input:
        fm_cfg: fm cfg

    Output:
        return station cfg according to fm cfg
    '''
    from random import randint
    # Get ssid
    station_cfg = dict(
        ssid       = fm_cfg['wlan_ssid'],
        # Get key_index
        key_index  =  fm_cfg.get('wep_key_idx',''), # <-> fm_cfg['wep_key_idx'] if fm_cfg.has_key('wep_key_idx') else None
        key_string = fm_cfg.get('wep_pass', ''),
        username   = fm_cfg.get('username', ''),
        password   = fm_cfg.get('password', ''),
    )

    wep_auto = ['open', 'shared']
    wpa_version = ['WPA', 'WPA2']
    wpa_auto = ['PSK', 'EAP']
    wpa_encryption = ['TKIP', 'AES']

    #if fm_cfg['encrypt_method'].lower() == 'disabled':
    # default is open system
    map_auth_cfg = dict(
        auth='open',
        encryption='none'
    )
    if fm_cfg['encrypt_method'].lower() == 'wep':
        map_auth_cfg = dict(
            encryption = {
                '5': 'WEP64',   # wep 64 bit 5 ascii
                '10': 'WEP64',  # wep 64 bit 10 hex
                '13': 'WEP128', # wep 128 bit 13 ascii
                '26': 'WEP128', # wep 128 bit 26 hex
            }[fm_cfg['encryption_len'].lower()],
            auth = {
                'open': 'open',
                'sharedkey': 'shared',
                'auto': wep_auto[randint(0,len(wep_auto)-1)],
            }[fm_cfg['wep_mode'].lower()],
        )
    elif fm_cfg['encrypt_method'].lower() == 'wpa':
        map_auth_cfg = dict(
            wpa_ver = {
                'wpa': 'WPA',
                'wpa2': 'WPA2',
                'auto': wpa_version[randint(0, len(wpa_version)-1)],
            }[fm_cfg['wpa_version'].lower()],
            encryption = {
                'tkip': 'TKIP', # wpa tkip algorithm
                'aes': 'AES',   #  wpa aes algorithm
                'auto': wpa_encryption[randint(0, len(wpa_encryption)-1)]
            }[fm_cfg['wpa_algorithm'].lower()],
            auth = {
                'psk': 'PSK',
                '802.1x': 'EAP',
                'auto': wpa_auto[randint(0,len(wpa_auto)-1)]
            }[fm_cfg['auth'].lower()],
            key_string = fm_cfg.get('psk_passphrase','')
        )

    station_cfg.update(map_auth_cfg)
    return station_cfg


UI_SUMMARY_KEYS = {
    # keys tile for WLAN Common
    'wirelessmode': 'wmode', #Wireless Mode
    'channel': 'channel',
    'countrycode': 'country_code',
    'channelwidth': 'channel_width',
    'transmitpower': 'txpower',
    'protectionmode': 'prot_mode',

    # keys title of Wlan detail table
    'name': "wlan_name", # Name
    'ssid': "wlan_ssid",
    'wirelessavailability': "avail", # Wireless Availability:
    'broadcastssid': "broadcast_ssid", # Broadcast SSID:
    'clientisolation': "client_isolation", # Client Isolation:
    'databeaconrate(dtim)': "dtim",#Data Beacon Rate(DTIM):           1
    'rts/ctsthreshold': "rtscts_threshold",

    # encryption method
    # if encryption method is disabled, its key is encryptionmode else mode
    # on the summary page
    'encryptionmode': "encrypt_method",
    'mode': "encrypt_method",

    # items for wep mode
    'authenticationmode': "wep_mode", # Open, Shared Key, Auto
    'encryptionstrength': "encryption_len", # 64bit 10hex digits
    'wepkey': "wep_pass",
    'keyindex': "wep_key_idx",

    # items for wpa mode
    'wpaversion': "wpa_version",
    'wpaalgorithm': "wpa_algorithm",
    'wpaauthentication': "auth",
    'passphrase': "psk_passphrase",
    # The summary page doesn't show information of Radius server
    # so don't define them here

    # Keys for FM Device View Internet/WAN Summary page
    'macaddress' : 'mac',
    'ipaddress': 'ip',
    'netmask': 'net_mask',
    'gateway': 'gateway',
    'primarydns': 'pri_dns',
    'secondarydns': 'sec_dns',
    'ntpserver': 'ntp_server',
    'internetconnectiontype': 'connection_type',
    'internetconnectionstatus': 'connection_status',
    'l2tpconnectionstatus': 'l2tp_status',

    # Keys for AP Web UI Internet Status. There are some keys the same with keys
    # from FM Device View Internet/WAN so ignore them, only define different titles.
    'mask': 'net_mask',
    'subnetmask': 'net_mask', # In version 9, it changes from Mask to subnet mask
    'primarydnsserver': 'pri_dns',
    'secondarydnsserver': 'sec_dns',
    'connectiontype': 'connection_type',
    'connectionstatus': 'connection_status',
}

# value items on UI Summary need to be converted
UI_SUMMARY_VALUES = {
    # wlan common items
    'prot_mode': {
        'cts-only': ".*CTS.*Only.*"
    },

    # wep items
    'wep_mode': {
        'sharedkey': ".*Shared.*Key.*",
    },
    # wpa items
    'wpa_version': {
        'auto': '.*WPA-AUTO.*',
    },

    # items of Internet/WAN summary page
    'connection_type': {
        'static': '.*Static.*',
        'dhcp':   '.*DHCP.*',
    }
}

def map_summary_to_provisioning_cfg(ui_summary_items):
    '''
    This function is to convert values gotten from Summary UI page to
    provisioning values as the cfgs in the libFM_TestSuite.
    NOTE: Convert keys first then values.
    '''
    # convert summary keys/values to provisioning keys/values
    provisioning_cfg = {}
    for k, v in ui_summary_items.iteritems():
        provisioning_k = UI_SUMMARY_KEYS[k]
        provisioning_cfg.setdefault(provisioning_k, v)

        if provisioning_k in UI_SUMMARY_VALUES:
            for cvK, cvI in UI_SUMMARY_VALUES[provisioning_k].iteritems():
                if re.match(cvI, provisioning_cfg[provisioning_k], re.I):
                    provisioning_cfg[provisioning_k] = cvK
                    break

    return provisioning_cfg

