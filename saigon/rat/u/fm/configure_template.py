'''
Do some action related to firmware upgrade (create/cancel/restart firmware upgrade task)
    + Create configuer template:
        + Go to Configure > AP Configure Templates
        + Click on "Create a template" link
        + Create a template according to your input configuration.
        + Click on "Save" button to save template

    + Copy configure template:
        + Go to Configure > AP Configure Templates
        + Click on "copy" link of Configure template that we want to copy.

    + Export configure template:
        + Go to Configure > AP Configure Templates
        + Click on "export" link of Configure template that we want to export.
            Choose "Save to disk" option when appearing a pop-up.



Examples:
tea.py u.fm.configure_template fm_ip_addr=97.74.124.173 fm_version='9' action=create_template template_name=test_create_template model=ZF7942 cfg={'device_general':{'device_name': 'test_name'}}
tea.py u.fm.configure_template fm_ip_addr=97.74.124.173 fm_version='9' action=copy_template template_name=test_create_template new_tmpl_name=my_new_tmpl
tea.py u.fm.configure_template fm_ip_addr=97.74.124.173 fm_version='9' action=export_template template_name=test_create_template

Note: You can define other configuration for the template (ex: Internet, Wireless Common, Wireless1)
Below are some hints for the configuration:
    + Internet: cfg={'internet' : {'gateway': "List of invalid value to check: enter three IPs like '1.1.1.1, 1.1.1.2, 1.1.1.3'",
                                   'conn_type': 'static, dynamic'
                                   'ip_addr': "List of invalid IPs to check: 1.1.1.-1, 1.1.1, 256.1.1.1",
                                   'mask': "List of invalid IPs to check: 255.255.255.256, 255.255.0, -255.255.255.0",}}
    + Wireless Common: cfg={'wlan_common' : {'channel':'SmartSelect', 'country_code':'United Kingdom',
                            'txpower':'Full', 'prot_mode':'Disabled'}}
    + Wireless1: cfg={'wlan_1': {
                            'wlan_num': 'Detail configuration for wlan_num (from 1 to 8)',
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
                            'cwep_pass': ' password of wep method (confirm)',

                            #WPA Version
                            'wpa_version': 'WPA version: WPA, WPA2, Auto',
                            #WPA Algorithm
                            'wpa_algorithm': 'WPA Algorithm: TKIP, AES, Auto',
                            #Authentication
                            'auth': 'Authentication: PSK, 802.1x, Auto',
                            'psk_passphrase': 'PSK passphrase',
                            'cpsk_passphrase': 'PSK passphrase (confirm)',
                            'radius_nas_id': 'Radius NAS-ID',
                            'auth_ip': 'Authentication IP address',
                            'auth_port': 'Authentication Port',
                            'auth_secret': 'Authentication Server Secret',
                            'cauth_secret': 'Authentication Server Secret',
                            'acct_ip': 'Accounting IP address',
                            'acct_port': 'Accounting Port',
                            'acct_secret': 'Accounting Server Secret',
                            'cacct_secret': 'Accounting Server Secret (confirm)'}}

'''



#from RuckusAutoTest.common.utils import get_cfg_items
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.scripts.fm import libFM_TestSuite as lib_fm_ts
from RuckusAutoTest.common import utils
from RuckusAutoTest.components import Helpers as lib

def create_template(tcfg):
    return lib.fm.cfg_tmpl.create_cfg_tmpl_2(tcfg['fm'], tcfg['template_name'],
                                      tcfg['model'], tcfg['cfg'])

def copy_cfg_template(tcfg):
    try:
        result = lib.fm.cfg_tmpl.copy_cfg_tmpl(tcfg['fm'], tcfg['template_name'], tcfg['new_tmpl_name'])
        if result:
            return "Copy template successful!!"
    except:
        return "Cant copy template"

def export_cfg_template(tcfg):
    return lib.fm.cfg_tmpl.export_cfg_tmpl(tcfg['fm'], tcfg['template_name'])

def do_config(tcfg):
    config = dict(
        fm_ip_addr = '192.168.30.252',
        model = 'ZF7942',
        fm_version = '8',
        template_name = 'test_firmware_upgrade',
        new_tmpl_name = 'new_template_name',
        action = 'create_template',
        cfg = {'device_general' : {'device_name': 'test_name'}}
    )
    config.update(tcfg)
    #if 'cfg' in tcfg:
    #   config['cfg'] = eval(tcfg['cfg'])


    # in report case, we don't need FM
    config['fm'] = create_fm_by_ip_addr(ip_addr = config.pop('fm_ip_addr'),
                                        version = config.pop('fm_version'))

    
    return config


def do_test(cfg):
    return {'create_template' : create_template,
            'copy_template' : copy_cfg_template,
            'export_template' : export_cfg_template}[cfg['action']](cfg)


def do_clean_up(cfg):
    clean_up_rat_env()

def main(**kwa):
    tcfg = do_config(kwa)
    #result = do_test(tcfg)
    do_clean_up(tcfg)

    #return result
