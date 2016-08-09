'''
The captive_portal tea is to demo the Captive Portal authentication using browser.
This tea supports:  
  - guest auth

It can run with a "brand new" ZD config, or with some existing one. In the latter case,
it will edit/update the configuration whenever possible, or try to create a new one
and continue if there exists that config.

Examples:
1. Basics with all default provided config in this tea. The "action" must be provided.   
   tea.py u.zd.captive_portal_guestpass      

2. With some personalized config: refer to "default_cfg" for accepted kwargs
   tea.py u.zd.captive_portal_guestpass action=web_auth sta_ip_addr="192.168.1.11"
'''

import copy
import logging

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_station_by_ip_addr,
    clean_up_rat_env,
)
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

user_cfg = {
    'username': "ras.local.user",
    'password': "ras.local.user",
}

guest_wlan_cfg = {
    'ssid': "rat-wlan-guestauth-123",
    'type': "guest",
    'auth': "open",
    'encryption': "none",
}

guest_auth_arg = {
    'guest_pass': "",
    'use_tou': False,
    'redirect_url': "",
    'no_auth': False,
    'target_url': "http://172.16.10.252/",
    'expected_data': "It works!",
}

sta_cfg = {
    'check_status_timeout': 120,
    'break_time': 10,
    'restart_cnt': 6,
}

gp_cfg = {
    'username': user_cfg['username'],
    'password': user_cfg['password'],
    'wlan': guest_wlan_cfg['ssid'],
    'type': 'single',
    'duration': '1',
    'duration_unit': 'Days',
    'guest_fullname': 'Tester',
    'remarks': '',
}

'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
default_cfg = {
    'zd_ip_addr': '192.168.0.2',
    'sta_ip_addr': '192.168.1.11',
    'user_cfg': user_cfg,    
    'guest_wlan_cfg': guest_wlan_cfg,
    'guest_auth_arg': guest_auth_arg,    
    'gp_cfg': gp_cfg,
}


def get_default_cfg():
    return copy.deepcopy(default_cfg)


def do_config(cfg):
    '''
    . get the default config
    . merge/update it to the user provided at runtime
    . check for action to perform
    . create the ZD
    . create the wireless station
    . start the browser on the station
    .
    '''
    _cfg = get_default_cfg()
    _cfg.update(cfg)

    _cfg['message'] = ""

    _cfg['zd'] = create_zd_by_ip_addr(default_cfg.pop('zd_ip_addr'))

    _cfg['sta'] = create_station_by_ip_addr(default_cfg.pop('sta_ip_addr'))

    # init the browser with default settings:
    # . browser = "firefox", tries = 3, timeout = 15
    # then start the browser
    _cfg['bid'] = _cfg['sta'].init_and_start_browser()

    return _cfg


def do_test(cfg):
    '''
    '''
    return _do_guest_auth_steps(cfg)

def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)

    res = None
    try:
        res = do_test(tcfg)

    except Exception, ex:
        print ex.message

    do_clean_up(tcfg)

    return res


def _do_guest_auth_steps(cfg):
    '''
    Full steps:
    . create a guest wlan
    . create a local user
    . generate a guest pass which is valid for one day
    . associate sta to the wlan
    . perform guest auth using browser in the sta
    '''
    zd = cfg['zd']
    sta = cfg['sta']

    # create a guest wlan
    wlan_cfg = cfg['guest_wlan_cfg']

    # for TEA, we don't need to create WLAN every time
    # just use the existing one with updated config
    wlan_name_list = lib.zd.wlan.get_wlan_list(zd)
    if not wlan_cfg['ssid'] in wlan_name_list:
        lib.zd.wlan.create_wlan(zd, wlan_cfg)

    else:
        lib.zd.wlan.edit_wlan(zd, wlan_cfg['ssid'], wlan_cfg)


    # create a local user
    user_cfg = copy.deepcopy(cfg['user_cfg'])
    user = lib.zd.user.get_user(zd, user_cfg['username'])
    if not user:
        user_cfg.update({
            'confirm_password': user_cfg['password'],
        })
        lib.zd.user.create_user(zd, user_cfg)


    # generate a guest pass
    gp_cfg = cfg['gp_cfg']
    lib.zd.ga.generate_guestpass(zd, **gp_cfg)
    guest_pass = lib.zd.ga.guestpass_info['single_gp']['guest_pass']


    # associate sta to the wlan
    tconfig.remove_all_wlan_from_station(sta)
    tmethod.assoc_station_with_ssid(
        sta, wlan_cfg, **sta_cfg
    )


    # perform guest authentication
    browser_id = cfg['bid']
    arg = cfg['guest_auth_arg']

    auth_arg = tconfig.get_guest_auth_params(
        zd, guest_pass, arg['use_tou'], arg['redirect_url']
    )
    auth_arg.update(arg)

    logging.info("Perform Guest Auth on the station %s" % cfg['sta_ip_addr'])
    messages = sta.perform_guest_auth_using_browser(browser_id, auth_arg)
    messages = eval(messages)

    errmsg = ""
    passmsg = ""
    for m in messages.iterkeys():
        if messages[m]['status'] == False:
            errmsg += messages[m]['message'] + " "

        else:
            passmsg += messages[m]['message'] + " "

    if errmsg:
        cfg['message'] = errmsg
        cfg['result'] = 'FAIL'
        return cfg

    cfg['result'] = 'PASS'
    cfg['message'] = passmsg + "Perform Guest Auth successfully on station [%s]." % cfg['sta_ip_addr']
    return cfg
