'''
The captive_portal tea is to demo the Captive Portal authentication using browser.
This tea supports:
  - web auth
  - guest auth
  - hotspot auth
  - download file

It can run with a "brand new" ZD config, or with some existing one. In the latter case,
it will edit/update the configuration whenever possible, or try to create a new one
and continue if there exists that config.

Examples:
1. Basics with all default provided config in this tea. The "action" must be provided.
   tea.py u.zd.captive_portal action=web_auth
   tea.py u.zd.captive_portal action=guest_auth
   tea.py u.zd.captive_portal action=hotspot_auth
   tea.py u.zd.captive_portal action=download_file

2. With some personalized config: refer to "default_cfg" for accepted kwargs
   tea.py u.zd.captive_portal action=web_auth sta_ip_addr="192.168.1.11"
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

hotspot_cfg = {
   'name': "Hotspot Profile - 1",
   'login_page': "http://192.168.0.250/login.html",
   'start_page': None,  # redirect to the URL that the user intends to visit.
   'auth_svr': "",      # Local Database as default
}

web_wlan_cfg = {
    'ssid': "rat-wlan-webauth-123",
    'auth': "open",
    'encryption': "none",
    'do_webauth': True
}

guest_wlan_cfg = {
    'ssid': "rat-wlan-guestauth-123",
    'type': "guest",
    'auth': "open",
    'encryption': "none",
}

hotspot_wlan_cfg = {
    'ssid': "rat-wlan-hotspot-123",
    'type': "hotspot",
    'auth': "open",
    'encryption': "none",
    'hotspot_profile': hotspot_cfg['name'],
}

web_auth_arg = {
    'target_url': "http://172.16.10.252/",
    'expected_data': "It works!",
}

guest_auth_arg = {
    'guest_pass': "",
    'use_tou': False,
    'redirect_url': "",
    'no_auth': False,
    'target_url': "http://172.16.10.252/",
    'expected_data': "It works!",
}

hotspot_auth_arg = {
    'redirect_url': "",
    'original_url': 'http://172.16.10.252/',
    'expected_data': "It works!",
}

download_file_arg = {
    'validation_url': "http://172.16.10.252/authenticated/",
    'download_loc': r"//a[@id='logo']",
    'file_name': "logo.zip",
    'page_title': "Ruckus Automation Test",
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
    'hotspot_cfg': hotspot_cfg,
    'web_wlan_cfg': web_wlan_cfg,
    'guest_wlan_cfg': guest_wlan_cfg,
    'hotspot_wlan_cfg': hotspot_wlan_cfg,
    'web_auth_arg': web_auth_arg,
    'guest_auth_arg': guest_auth_arg,
    'hotspot_auth_arg': hotspot_auth_arg,
    'download_file_arg': download_file_arg,
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

    if not _cfg.get('action'):
        raise Exception('Please provide your action ["web_auth", '\
                        '"guest_auth", "hotspot_auth", "download_file"]')

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
    return {
        'web_auth' : _do_web_auth_steps,
        'guest_auth' : _do_guest_auth_steps,
        'hotspot_auth' : _do_hotspot_auth_steps,
        'download_file' : _do_download_file,
    }[cfg['action']](cfg)


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


def _do_web_auth_steps(cfg):
    '''
    Full steps:
    . create a web wlan
    . create a local user
    . associate sta to the wlan
    . perform web auth using browser in the sta
    '''
    zd = cfg['zd']
    sta = cfg['sta']

    # create a standard wlan with web auth enabled
    wlan_cfg = cfg['web_wlan_cfg']

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


    # associate sta to the wlan
    tconfig.remove_all_wlan_from_station(sta)
    tmethod.assoc_station_with_ssid(
        sta, wlan_cfg, **sta_cfg
    )


    # perform web authentication
    browser_id = cfg['bid']
    arg = cfg['web_auth_arg']

    auth_arg = tconfig.get_web_auth_params(
        zd, user_cfg['username'], user_cfg['password']
    )
    auth_arg.update(arg)

    logging.info("Perform Web Auth on the station %s" % cfg['sta_ip_addr'])
    messages = sta.perform_web_auth_using_browser(browser_id, auth_arg)
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
    cfg['message'] = passmsg + "Perform Web Auth successfully on station [%s]." % cfg['sta_ip_addr']
    return cfg


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


def _do_hotspot_auth_steps(cfg):
    '''
    Full steps:
    . create a hotspot service which uses local DB for authentication
    . create a local user
    . create a hotspot wlan
    . associate sta to the wlan
    . perform web auth using browser in the sta
    '''
    zd = cfg['zd']
    sta = cfg['sta']

    # create a hotspot service
    hotspot_cfg = cfg['hotspot_cfg']
    try:
        lib.zd.wispr.create_profile(zd, **hotspot_cfg)

    except Exception, ex:
        if "already exists" in ex.message:
            pass

    # create a local user
    user_cfg = copy.deepcopy(cfg['user_cfg'])
    user = lib.zd.user.get_user(zd, user_cfg['username'])
    if not user:
        user_cfg.update({
            'confirm_password': user_cfg['password'],
        })
        lib.zd.user.create_user(zd, user_cfg)


    # create a hotspot wlan
    wlan_cfg = cfg['hotspot_wlan_cfg']

    # for TEA, we don't need to create WLAN every time
    # just use the existing one with updated config
    wlan_name_list = lib.zd.wlan.get_wlan_list(zd)
    if not wlan_cfg['ssid'] in wlan_name_list:
        lib.zd.wlan.create_wlan(zd, wlan_cfg)

    else:
        lib.zd.wlan.edit_wlan(zd, wlan_cfg['ssid'], wlan_cfg)


    # associate sta to the wlan
    tconfig.remove_all_wlan_from_station(sta)
    tmethod.assoc_station_with_ssid(
        sta, wlan_cfg, **sta_cfg
    )


    # perform hotspot authentication
    browser_id = cfg['bid']
    arg = cfg['hotspot_auth_arg']

    auth_arg = tconfig.get_hotspot_auth_params(
        zd, user_cfg['username'], user_cfg['password'], arg['redirect_url']
    )
    auth_arg.update(arg)

    logging.info("Perform Hotspot Auth on the station %s" % cfg['sta_ip_addr'])
    messages = sta.perform_hotspot_auth_using_browser(browser_id, auth_arg)
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
    cfg['message'] = passmsg + "Perform Hotspot Auth successfully on station [%s]." % cfg['sta_ip_addr']
    return cfg


def _do_download_file(cfg):
    '''
    Full steps:
    . must be called after any of the auth steps above
    . perform download file using browser in the sta
    '''
    sta = cfg['sta']

    # perform hotspot authentication
    browser_id = cfg['bid']
    arg = cfg['download_file_arg']
    auth_arg = arg

    messages = sta.download_file_on_web_server(browser_id, **auth_arg)
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
    cfg['message'] = passmsg + "The file %s was downloaded successfully to the station [%s]." % (arg['file_name'], cfg['sta_ip_addr'])
    return cfg


