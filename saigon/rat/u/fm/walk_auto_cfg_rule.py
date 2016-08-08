'''
This tea is to walk through auto config rule for all aps
. cfg_2.4G_1: Verify following things
        "Device General, Wlan Common, Encryption type ['wep_open_5_ascii',
        'wep_open_10_hex', 'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex']
        on wlans [2, 4, 6, 8]

. cfg_2.4G_2: Verify following things
        "Encryption type ['wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk',
        'wpa_aes_802.1x', 'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk',
        'wpa2_aes_802.1x'] on wlans [1, 2, 3, 4, 5, 6, 7, 8]"

.cfg_5G_1: Verify following things:
        "Device General, Wlan Common, Encryption type ['wep_open_5_ascii',
        'wep_open_10_hex', 'wep_sharedkey_13_ascii', 'wep_sharedkey_26_hex']
        on wlans [10, 12, 14, 16]"

.cfg_5G_2: Verify following things:
        "Encryption type ['wpa_tkip_psk', 'wpa_tkip_802.1x', 'wpa_aes_psk',
        'wpa_aes_802.1x', 'wpa2_tkip_psk', 'wpa2_tkip_802.1x', 'wpa2_aes_psk',
        'wpa2_aes_802.1x'] on wlans [9, 10, 11, 12, 11, 12, 13, 14, 15, 16]"

Examples:
tea.py u.fm.walk_auto_cfg_rule fm_ip='192.168.0.124' version=9 ap_ip='192.168.0.199' model=ZF2741 radio_mode=2.4g cfg_id=cfg_2.4g_1
tea.py u.fm.walk_auto_cfg_rule fm_ip='192.168.0.124' version=9 ap_ip='192.168.0.236' model=ZF2741 radio_mode=2.4g cfg_id=cfg_2.4g_2
tea.py u.fm.walk_auto_cfg_rule fm_ip='192.168.0.124' version=9 ap_ip='192.168.0.236' model=ZF7962 radio_mode=5g cfg_id=cfg_5g_1
tea.py u.fm.walk_auto_cfg_rule fm_ip='192.168.0.124' version=9 ap_ip='192.168.0.236' model=ZF7962 radio_mode=5g cfg_id=cfg_5g_2
'''

import logging
import copy
import re
from pprint import pformat

from RuckusAutoTest.scripts.fm.libFM_DevCfg import get_ap_test_cfg_tmpl
from RuckusAutoTest.common.utils import get_timestamp, log_trace, \
                                        try_times, compare_dict
from RuckusAutoTest.tests.fm.lib_FM import set_ap_serial, set_ap_factory, \
                                           wait4_ap_stable, get_ap_default_cli_cfg
from RuckusAutoTest.components import (
    create_fm_by_ip_addr, clean_up_rat_env, create_ap_by_model
)
from RuckusAutoTest.tests.fm.lib_FM import wait4_ap_up, get_ap_serial, reboot_ap
from RuckusAutoTest.components import Helpers as lib

errmsg = None

def do_config(cfg):
    p = _cfg_test_params(cfg)
    logging.info('Test params: %s' % pformat(p))
    return p


def do_test(cfg):

    _create_cfg_tmpl(cfg)
    if errmsg: return dict(result='ERROR', message=errmsg)

    _create_auto_cfg_rule(cfg)
    if errmsg: return dict(result='ERROR', message=errmsg)

    _change_ap_serial(cfg)
    if errmsg: return dict(result='ERROR', message=errmsg)

    _set_ap_fm_url(cfg)
    if errmsg: return dict(result='ERROR', message=errmsg)

    _is_device_marked_auto_config(cfg)
    if errmsg: return dict(result='ERROR', message=errmsg)

    _is_device_auto_configured_by_rule(cfg)
    if errmsg: return dict(result='ERROR', message=errmsg)

    _verify_ap_webui(cfg)
    if errmsg: return dict(result='ERROR', message=errmsg)

    return dict(
        result='PASS',
        message='Auto config test for model "%s" with config "%s" work correctly'
        % (cfg['model'], cfg['test_name'])
    )


def do_clean_up(p):
    logging.info('Cleaning up the test...')
    _stop_auto_cfg_rule(p)
    _disable_auto_configured_device(p)
    _restore_ap_serial(p)
    _reset_ap_factory(p)
    _set_ap_fm_url(p)
    p['fm'].logout()
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res


def _cfg_test_params(cfg):
    p = dict(
        fm_ip  = '192.168.20.252',
        ap_ip  = '192.168.20.124',
        model = 'ZF2741',
        radio_mode = '2.4g',
        cfg_id = 'cfg_2.4g_1',
        input_cfg = {},
        test_name = '',
        device_group = 'All Standalone APs',
        version = '8',
    )
    p.update(cfg)

    # Get list of test cfg base on model and radio
    list_test_cfg = get_ap_test_cfg_tmpl([p['model']], p['radio_mode'])
    # idx of needed cfg from the list
    cfg_idx = {
        'cfg_2.4g_1': 0,
        'cfg_2.4g_2': 1,
        'cfg_5g_1': 0,
        'cfg_5g_2': 1,
    }[p['cfg_id'].lower()]

    p['input_cfg'] = list_test_cfg[p['model'].upper()][cfg_idx]['cfg']
    p['test_name'] = list_test_cfg[p['model'].upper()][cfg_idx]['cfg_name']
    time_stamp = get_timestamp()
    # Add basic param to do test cfg upgrade for
    # Basic param 1: create a config param for cfg template
    # Add basic param to do test cfg upgrade for
    # Basic param 1: create a config param for cfg template
    p.update(
        tmpl_cfg = dict(
            template_name = 'tea_auto_cfg_tmpl_%s_%s' % (p['model'], time_stamp),
            template_model = p['model'].upper(),
            options = p['input_cfg'],
        )
    )
    # cfg for the rule
    p.update(
        rule_cfg = dict(
            cfg_rule_name = 'tea_auto_cfg_%s_%s' % (p['model'], time_stamp),
            device_group = p['device_group'],
            model = p['model'].upper(),
            cfg_template_name = p['tmpl_cfg']['template_name'],
            create_time = '', # will be updated in _create_auto_cfg_rule
        )
    )
    # Create FM instance
    p['fm'] = create_fm_by_ip_addr(ip_addr=cfg.pop('fm_ip'), version=p['version'])
    p['ap'] = create_ap_by_model(p['model'], p['ap_ip'])

    # generate one new serial
    p['new_serial'] = p['fm'].generate_unique_ap_serials(**{'no': 1, 'prefix': 'ZF'})[0]
    p['ori_serial'] = get_ap_serial(**{'config':{'ip_addr': p['ap_ip']}})

    return p

def _create_cfg_tmpl(p):
    try:
        lib.fm.cfg_tmpl.create_cfg_tmpl_2(
            p['fm'], p['tmpl_cfg']['template_name'],
            p['tmpl_cfg']['template_model'], p['tmpl_cfg']['options']
        )
        logging.info('Created a template "%s" successfully' % p['tmpl_cfg']['template_name'])
    except Exception, e:
        log_trace()
        _fill_error_msg(p, e.__str__())

def _create_auto_cfg_rule(p):
    '''
    Create an auto configuration rule for this group
    '''
    # logging.info('Create an Auto Config Rule for model %s' % p['model'])
    delta = 0
    try:
        r_cfg = p['rule_cfg']
        p['rule_cfg']['create_time'] = lib.fm.auto_cfg.create_auto_cfg_rule(
            p['fm'], r_cfg['cfg_rule_name'], r_cfg['device_group'],
            r_cfg['model'], r_cfg['cfg_template_name'], advance_return=True
        )
        logging.info('Created an auto config rule "%s" for the test' % r_cfg['cfg_rule_name'])
    except Exception, e:
        log_trace()
        _fill_error_msg(p, e.__str__())

def _change_ap_serial(p):
    ''''''
    config= {
        'ip_addr': p['ap_ip']
    }
    logging.info('Change serial of AP %s to %s' % (config['ip_addr'], p['new_serial']))
    if not set_ap_serial(**{'serial': p['new_serial'], 'config': config}):
        _fill_error_msg(p,
            'Cannot set a new serial %s for AP %s' %
            (p['new_serial'], config['ip_addr'])
        )
        return

    # just reboot to make new serial take effect to save time, don't need to set factory
    #logging.info('Reboot the AP %s to make new serial take effect' % ap['ip_addr'])
    if not reboot_ap(config):
        _fill_error_msg(p,
            'Cannot reboot AP %s after change its serial' % (config['ip_addr'])
        )
        return

    if not wait4_ap_up(**{'config':config}):
        _fill_error_msg(p,
             'The AP %s is not boot up...' % (config['ip_addr'])
        )
        return

def _set_ap_fm_url(p):
    '''
    This function is to set FM server url for each AP
    '''
    fm_url = 'https://%s/intune/server' % p['fm'].get_cfg()['ip_addr']
    _wait_for_ap_cpu_free(p)
    try:
        p['ap'].start(15)
        #ap.set_fm_url(url=fm_url, validate_url=False)
        lib.ap.acc.set(
                p['ap'],
                cfg=dict(remote_mode='auto', fm_url=fm_url, inform_interval='5ms')
            )
    except Exception, e:
        log_trace()
        _fill_error_msg(p, e.__str__())

    p['ap'].stop()

def _is_device_marked_auto_config(p):
    '''
    This function is to test whether FM marks a device as "Auto Configured" with "check" symbol
    '''
    logging.info('Test to make sure tested devices marked as Auto Configured')
    try:
        lib.fm.auto_cfg.is_device_marked_auto_config(p['fm'], p['new_serial'])
    except Exception, e:
        log_trace()
        _fill_error_msg(p, e.__str__())

def _is_device_auto_configured_by_rule(p):
    '''
    This function is to test whether FM marks a device as "Auto Configured" with "check" symbol
    '''
    logging.info('Test to make sure tested devices are auto configured by the expected rule')
    try:
        if not lib.fm.auto_cfg.is_device_auto_configured_by_rule(
            p['fm'], p['new_serial'],
            p['rule_cfg']['cfg_rule_name'], p['rule_cfg']['create_time']
        ):
            _fill_error_msg(p,
                'ERROR: The device with serial %s is not auto configured by the rule %s' %
                (p['new_serial'], p['rule_cfg']['cfg_rule_name'])
            )
        else:
            logging.info('CORRECT! The device with serial %s is auto configured by the first rule %s' %\
                             (p['new_serial'], p['rule_cfg']['cfg_rule_name']))
    except Exception, e:
        _fill_error_msg(p, e.__str__())

def _stop_auto_cfg_rule(p):
    '''
    To stop an auto cfg rule
    '''
    try:
        r_cfg = p['rule_cfg']
        logging.info('Trying to stop the rule %s' % r_cfg['cfg_rule_name'])

        lib.fm.auto_cfg.stop_auto_cfg_rule(
            p['fm'], r_cfg['cfg_rule_name'], r_cfg['create_time']
        )
    except Exception, e:
        logging.info(
            'Warning: Cannot stop the rule %s. Error: %s' % (r_cfg['cfg_rule_name'], e.__str__())
        )

def _disable_auto_configured_device(p):
    '''
    After finish the test we need to disable tested APs with new serial
    so that they are not shown on Inventory > Manage Device
    '''
    try:
        lib.fm.dreg.set_device_status(
            p['fm'], p['new_serial'], "Unavailable", 'Automation changed to Unavailable'
        )
    except Exception, e:
        logging.debug(
            'Warning: Cannot disable the device %s' % p['new_serial']
        )

def _wait_for_ap_cpu_free(p):
    '''
    This function is to check CPU usage of AP and wait for each ready to test.
    Note: if provide username password, this function will use that username/password
    instead of username/password from ap instance to connect to AP and monitor its CPU usage.
    '''
    # monitor AP CPU usage to wait for its load < 40% after rebooting or provisioning
    MONITOR_CPU_USAGE = 0

    monitor_cpu_cfg= {
        #'config': config,
        'monitor': MONITOR_CPU_USAGE,
        'threshold': 10, # default % CPU Usage
        'timeout': 20, # in minute
        'interval': 2,
        'times_to_check': 3,
    }

    monitor_cpu_cfg.update(dict(config={'ip_addr': p['ap_ip']}))
    msg = 'CPU of AP %s looks free for the test' % p['ap_ip']\
            if wait4_ap_stable(**monitor_cpu_cfg) else \
            ('WARNING: The CPU usage of AP %s is still too high' % p['ap_ip'])
    logging.info(msg)

def _wait_for_ap_ready(p):
    '''
    This function will check if provision some configuration items which
    require AP rebooted. In this case it will sleep a moment to wait for
    AP ready to use again.
    Note: Current we only have some items which take time to provision.
        1. 'wmode', 'country_code': take time to reboot
        2. 'downlink', 'uplink': Rate Limiting takes time to apply.

        If there are more items, we will add more
    '''
    k = 'wlan_common' #a.cfm['PRO_WLAN_COMMON_TITLE']
    item1 = 'wmode'
    item2 = 'country_code'

    logging.info('Wait for AP ready to test')

    # NOTE: currently we will not change username/password of the test. To avoid
    # the test failed, it will affect other tcs so we don't need to check changed
    # username/password here.

    # change_username, change_password = None, None
    # If user changed user and password, need to assign new username and password to AP
    # if p['input_cfg'].has_key('device_general'):
    #    #if provisioned_cfg_options['device_general'].has_key('username'):
    #    change_username = p['input_cfg']['device_general'].get('username', None)
    #    change_password = p['input_cfg']['device_general'].get('password', None)

    if p['input_cfg'].has_key(k) and \
       (p['input_cfg'][k].has_key(item1) or\
       p['input_cfg'][k].has_key(item2)):
        # sleep to wait for the first AP enter into reboot progress.
        logging.info('The test requires AP reboot...')
        config = get_ap_default_cli_cfg()
        ap_config = p['ap'].get_cfg()
        config.update(ap_config)
        #config['ip_addr'] = ap_config['ip_addr']
        #config['username'] = ap_config['username'] if not change_username else change_username
        #config['password'] = ap_config['password'] if not change_password else change_password
        if not wait4_ap_up(**{'config': config, 'timeout': 6}):
            errmsg += 'Cannot login to AP via cli %s after 6 mins waiting' \
                            % (config['ip_addr'])

    _wait_for_ap_cpu_free(p)

'''
def _set_ap_mgmt_mode(p, mode):
    ''''''
    try:
        logging.info('Set management type of ap %s to %s' % (p['ap_ip'], mode))
        _wait_for_ap_cpu_free()
        p['ap'].start(15)
        lib.ap.acc.set(ap, cfg=dict(remote_mode=mode))
    except Exception, e:
        log_trace()
        _fill_error_msg(p, e.__str__())
    # Sleep a moment before stop ap to make sure the changes are submitted completely
    time.sleep(2.5)
    p['ap'].stop()
    _wait_for_ap_cpu_free(p)
'''

def _filter_unused_keys_on_ap(fm_cfg):
    '''
    This function is to remove unnecessary items of WLAN detail before doing
    the comparison with info got from AP.
    Input:
    - kwargs is the list of WLAN Det parameters
    '''
    removed_items = ['client_isolation', 'rate_limiting', 'cwep_pass',
                    'cpsk_passphrase', 'cauth_secret', 'cacct_secret', 'wlan_num']

    options = copy.deepcopy(fm_cfg)
    MAX_WLAN = 16
    # Remove unnecessary for wlan 1 to 8
    for i in range(1,MAX_WLAN+1):
        k = 'wlan_%d' % i # a.cfm['PRO_WLAN_%d_TITLE' % i]
        if options.has_key(k):
            # Add necessary items first
            #if temp.has_key('rate_limiting') and temp['rate_limiting'].lower() == 'disabled':
            #    # Add uplink/donwlink key for commparison
            #    # Zero is value of uplink/downlink when Rate Limiting is DISABLED
            #    temp['downlink'], temp['uplink'] = '0', '0'

            # Then remove unused items for comparison
            for item in removed_items:
                if options[k].has_key(item): del options[k][item]

    removed_items = ['password', 'cpassword']
    k = 'device_general' # a.cfm['PRO_DEV_GENERAL_TITLE']
    if options.has_key(k):
        for item in removed_items:
            if options[k].has_key(item): del options[k][item]

    return options

def _verify_ap_webui(p):
    ''''''
    logging.info('Verify AP web ui after provision cfg from FM')
    _wait_for_ap_cpu_free(p)
    # TODO: currently, makefmtestbed only supports to add one ap for each test.
    # Hence, we need to consider supporting to verify more than one ap here
    fm_cfg, MAX_RETRIES = p['input_cfg'], 3
    fm_cfg = _filter_unused_keys_on_ap(fm_cfg)
    radio_mode = {
        '2.4G': lib.ap.wlan.DUAL_BAND_RD_MODE_1,
        '5G': lib.ap.wlan.DUAL_BAND_RD_MODE_2,
    }[p['radio_mode'].upper()]

    p['ap'].start(15)
    #tmp = ap._tmp_[timestamp]
    for k, v in fm_cfg.iteritems():
        print 'v: %s' % v
        for i in try_times(MAX_RETRIES, 20):
            msg, fm_v = None, copy.deepcopy(v)
            try:
                if 'device_general' == k:
                    ap_v = lib.ap.dev.get(p['ap'], fm_v.keys())
                elif 'wlan_common' == k:
                    # ap_v = lib.ap.wlan.getWLANCommon(ap, fm_v.keys(), True, True)
                    ap_v = lib.ap.wlan.get_wlan_common(
                        p['ap'], fm_v.keys(), True, True, radio_mode
                    )
                elif 'wlan' in k:
                    # for wlan 1 to 8
                    wlan_no = int(int(re.search('\d+', k).group(0)))
                    #ap_v = lib.ap.wlan.getWLAN(ap, wlan_no, fm_v.keys(), True, True)
                    ap_v = lib.ap.wlan.get_wlan_detail(
                        p['ap'], wlan_no, fm_v.keys(), True, True, radio_mode
                    )
                else:
                    raise Exception('Unsupport this key "%s"' % k)
                logging.info('Verifying option: %s. \nInput cfg: %s. \nAP cfg: %s' %
                             (k, pformat(fm_v), pformat(ap_v)))
                msg = compare_dict(fm_v, ap_v, tied_compare=False)
            except Exception, e:
                msg = e.__str__()
                log_trace()
            if not msg:
                    break
            elif i < MAX_RETRIES:
                logging.info('Found error: %s. Sleep a moment a try again...' %
                             pformat(msg))
            else:
                _fill_error_msg(p, msg)

        if errmsg:
            break

    p['ap'].stop()
    if not errmsg:
        logging.info('All APs are upgraded successully')
        _fill_pass_msg(p)


def _fill_error_msg(p, errmsg):
    errmsg = 'The test "%s" has error:" %s' % (p['test_name'], errmsg)
    logging.info(errmsg)


def _fill_pass_msg(p):
    passmsg = 'The test "%s" works correctly' % p['test_name']
    logging.info(passmsg)


def _reset_ap_factory(p):
    ''''''
    logging.info('Reset factory the test ap...')
    # Next, wait for the test AP boot up
    ap_cli_cfg = get_ap_default_cli_cfg()
    ap_cli_cfg.update(p['ap'].get_cfg())
    if not set_ap_factory(config=ap_cli_cfg):
            logging.info('Warning: Cannot set factory the test AP')


def _set_fm_url(p):
    ''''''
    try:
        p['ap'].start(15)
        fm_url = 'http://%s/intune/server' % p['fm'].get_cfg()['ip_addr']
        logging.info('Set fm url %s for the test ap' % fm_url)
        _wait_for_ap_cpu_free(p)
        p['ap'].start(15)
        lib.ap.acc.set(p['ap'], dict(fm_url=fm_url))
        p['ap'].stop()
    except Exception, e:
        log_trace()
        logging.info('Warning: Unexpected error happens: %s' % e.__str__())

def _restore_ap_serial(p):
    '''
    Restore ogriginal serials for all APs
    '''
    logging.info(
        'Restoring original serial %s for AP %s' %
        (p['ori_serial'], p['ap_ip'])
    )
    config= {'ip_addr': p['ap_ip']}

    if not set_ap_serial(**{'serial': p['ori_serial'], 'config': config}):
        logging.info(
            'Warning: Cannot restore the original serial %s for AP %s' %
            (p['ori_serial'], p['ap_ip'])
        )
        return
