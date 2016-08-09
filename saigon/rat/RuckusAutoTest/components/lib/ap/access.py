'''
This module covers 2 AP pages: Admin > Management and Admin > Log
'''

import re
import time

from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, get as ac_get
from RuckusAutoTest.components.lib.fm import config_mapper_fm_old as cfgMapper


Locators = dict(
    # Access Mgmt are on Admin > Mgmt page
    telnet_enabled = Ctrl(
        dict(enabled = "//input[@id='telnet-y']",
             disabled = "//input[@id='telnet-n']",
        ), type = 'radioGroup'),
    telnet_port = Ctrl("//input[@id='telnetport']"),

    ssh_enabled = Ctrl(
        dict(enabled = "//input[@id='ssh-y']",
             disabled = "//input[@id='ssh-n']",
        ), type = 'radioGroup'),
    ssh_port = Ctrl("//input[@id='sshport']"),

    http_enabled = Ctrl(
        dict(enabled = "//input[@id='http-y']",
             disabled = "//input[@id='http-n']",
        ), type = 'radioGroup'),
    http_port = Ctrl("//input[@id='httpport']"),

    https_enabled = Ctrl(
        dict(enabled = "//input[@id='https-y']",
             disabled = "//input[@id='https-n']",
        ), type = 'radioGroup'),
    https_port = Ctrl("//input[@id='httpsport']",),

    remote_mode = Ctrl(
        dict(auto = "//input[@id='remote_management_mode_0']",
             fm = "//input[@id='remote_management_mode_1']",
             snmp = "//input[@id='remote_management_mode_2']",
             none = "//input[@id='remote_management_mode_3']",
        ), type = 'radioGroup'),

    dhcp_fm_url = Ctrl("//tr[contains(./th,'DHCP')]/td", type = 'html'),
    fm_url = Ctrl("//input[@id='tr069dnsmapurl']"),

    # Tu Bui: change to fix bug when running FM
    tr069_username = Ctrl("//input[@id='tr069_acs_calls_cpe_username']", type = 'text'),
    tr069_password = Ctrl("//input[@id='tr069_acs_calls_cpe_password']", type = 'text'),
    inform_interval = Ctrl("//select[@id='tr069periodicinforminterval']", type = 'select'),
    # tr069 status table
    tr069_status = Ctrl("//table[@id='tr069_options2']", type = '_htable', cfg = dict(ignore_case = True)),

    # Log configs are on Admin > Log
    log_enabled = Ctrl(
        dict(enabled = "//input[@id='enablelog-y']",
             disabled = "//input[@id='enablelog-n']",
        ), type = 'radioGroup'),
    log_ip = Ctrl(
        ("//input[@id='sysloghost0']",
         "//input[@id='sysloghost1']",
         "//input[@id='sysloghost2']",
         "//input[@id='sysloghost3']",
        ), type = 'ipGroup'),
    log_port = Ctrl("//input[@id='sysloghostport']"),
    logs = Ctrl("//pre[@id='currentlog']", type = 'html'),

    # submit_btn is now used for both Admin > Mgmt, Admin > Log pages
    submit_btn = "//input[@id='submit-button']",
)


OrderedCtrls = ('telnet_enabled', 'ssh_enabled', 'http_enabled',
                'https_enabled', 'log_enabled')


CtrlsByPage = dict(
    # Access Mgmt are on Admin > Mgmt page
    mgmt = ('telnet_enabled', 'telnet_port', 'ssh_enabled', 'ssh_port',
          'http_enabled', 'http_port', 'https_enabled', 'https_port',
          'remote_mode', 'dhcp_fm_url', 'fm_url', 'tr069_username',
          'tr069_password', 'inform_interval', 'tr069_status',
    ),
    # Log configs are on Admin > Log
    log = ('log_enabled', 'log_ip', 'log_port', 'logs',),
)

# Constants for this module
TR069_STATUS_INFORM_SUCCESS = 0
# no inform sent from AP
TR069_STATUS_NO_INFORM = 1
# it sends inform but failed
TR069_STATUS_INFORM_FAIL = 2


def nav_to(obj, page = 'mgmt', force = False):
    p = dict(
        mgmt = obj.ADMIN_MGMT,
        log = obj.ADMIN_LOG,
    )[page]
    obj.navigate_to(obj.MAIN_PAGE, p, force = force)


def _split_cfg_by_page(cfg, is_set = True):
    '''
    since this module deals with 2 pages at a time, cfg is splitted
    to 2 parts accordingly
    '''
    p = CtrlsByPage
    if is_set:
        return dict(
            mgmt = dict([(i, cfg[i]) for i in cfg if i in p['mgmt']]),
            log = dict([(i, cfg[i]) for i in cfg if i in p['log']]),
        )
    else: # else is here for improving reading
        return dict(
            mgmt = [i for i in cfg if i in p['mgmt']],
            log = [i for i in cfg if i in p['log']],
        )


def get(obj, cfg_ks):
    s, l = obj.selenium, Locators
    cfg = {}
    for k, v in _split_cfg_by_page(cfg_ks, is_set = False).iteritems():
        #log('k: %s, v: %s' % (k, v))
        if len(v):
            nav_to(obj, k, force = True)
            cfg.update(cfgMapper.map_cfg_value(ac_get(s, l, v), toSelect = False))
    return cfg


def set(obj, cfg):
    s, l, oc = obj.selenium, Locators, OrderedCtrls
    cfg = cfgMapper.map_cfg_value(cfg, toSelect = True)
    for k, v in _split_cfg_by_page(cfg).iteritems():
        if len(v):
            nav_to(obj, k, force = True)
            ac_set(s, l, v, oc)
            s.safe_click(l['submit_btn'])
            s.wait_for_page_to_load()


def reset(obj, cfg_ks):
    s, d = obj.selenium, obj.access_mgmt
    # NOTE
    #   fm_url once set cannot be restored to blank,
    #   keep the dhcp_fm_url as the default value
    cfg = dict([(k, d[k]) for k in cfg_ks])
    if 'fm_url' in cfg_ks:
        cfg['fm_url'] = get_item(obj, 'dhcp_fm_url')
    return set(obj, cfg)


def get_item(obj, item):
    return get(obj, [item])[item]


def get_tr069_status_msg(obj):
    '''
    This function is to get tr069 status htable. It returns tr069 status table like
    function get_htable_content().
    '''
    return get_item(obj, 'tr069_status')


def get_inform_interval(obj):
    '''
    Get inform interval and map to input value format and return it
    '''
    return get_item(obj, 'inform_interval')


def set_inform_interval(obj, interval_str):
    '''
    Get inform interval and map it to input value format and return it
    '''
    k = 'inform_interval'
    return set(obj, {k: interval_str})


def interval_str_to_sec(str):
        '''
        This function is to convert inform interval to second. Its format interval
        as below:
            + In minutes: 1m, 5ms, 10ms, 15ms, 30ms
            + In hour: 1h, 4hs, 12hs, 24s
            + In week: 1w, 2ws, 4ws
        '''
        # get the numer from interval string
        num = re.search('\d+', str).group(0)
        # get the numer from interval string
        unit = re.search('\D+', str).group(0)
        multiplier = {
            'm': 60, # min
            'h': 60 * 60, # hour
            'w': 60 * 60 * 24 * 7, #week: 60(sec)x60(mins)*24(hours)*7(days)
        }[unit[0]]

        return int(num) * multiplier


def _time_str_to_time_obj(raw_time_str, pattern, time_format):
    '''
    This function is to extract time from a string then convert the time in string
    to a time object. After that, we can use this object to compare the time.
    @ TODO: Consider to move this function to utils lib
    '''
    time_str = re.search(pattern, raw_time_str, re.I).group(0)
    struct_time = time.strptime(time_str, time_format)
    # create time object from struct_time
    return time.mktime(struct_time)


def get_tr069_inform_status(obj):
    '''
    This function is to check whether the AP calls home successfully with current
    inform interval.
    1. get current interval
    2. convert to second
    3. get last attempted contact
    4. get last success contact
    5. get current time.
    6. Calculate:
        delta 1 = current time and last attempted contact
        delta 2 =  last attempted contact and last success contact
    Return:
    - (0, tr069 status msg): Success
    - (1, tr069 status msg): don't call home
    - (2, tr069 status msg): call home but failed

    A fail message:
        sendInform failed: No Inform done (9890) SOAP 1.1 fault: SOAP-ENV:Client
        [(none)] "Operation interrupted or timed out" Detail: (none)
    '''
    interval = interval_str_to_sec(get_inform_interval(obj))
    tr069_status_msg = get_tr069_status_msg(obj)

    # last attempted contact time looks like:
    # 2009-06-25 08:44:33 GMT using https://192.168.0.124/intune/server
    p, format = '.*(?= GMT)', '%Y-%m-%d %H:%M:%S'
    la = _time_str_to_time_obj(tr069_status_msg['lastattemptedcontact'], p, format)
    # last success contact time also looks like:
    # 2009-06-25 08:44:33 GMT using https://192.168.0.124/intune/server
    p, format = '.*(?= GMT)', '%Y-%m-%d %H:%M:%S'
    ls = _time_str_to_time_obj(tr069_status_msg['lastsuccessfulcontact'], p, format)
    # current time looks like: Thu Jun 25 08:44:59 2009 (UTC)
    p, format = '.*(?= \(UTC\))', '%a %b %d %H:%M:%S %Y'
    ct = _time_str_to_time_obj(tr069_status_msg['currenttime'], p, format)

    status = TR069_STATUS_INFORM_SUCCESS

    if la - ls > interval or \
       'successful' != tr069_status_msg['lastcontactresult'].strip().lower():
        status = TR069_STATUS_INFORM_FAIL
    elif ct - la > interval:
        status = TR069_STATUS_NO_INFORM

    return status, tr069_status_msg

