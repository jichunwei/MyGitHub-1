'''
#------------------------------------------------------------------------------
IMPORTANT:
This tea to support following functions in Configure > ZoneDirectors > Config Templates
 . create
 . edit
 . delete
#------------------------------------------------------------------------------

Examples to do other functions: query, edit, delete
tea.py u.fm.zd_cfg_tasks fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=create prov_to=device schedule=0
tea.py u.fm.zd_cfg_tasks fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=create prov_to=view schedule=0
tea.py u.fm.zd_cfg_tasks fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=create prov_to=device schedule=5
tea.py u.fm.zd_cfg_tasks fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=restart prov_to=device schedule=5
tea.py u.fm.zd_cfg_tasks fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=delete prov_to=device schedule=5
tea.py u.fm.zd_cfg_tasks fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=cancel prov_to=device schedule=5
'''

import logging
import time
from pprint import pformat
from RuckusAutoTest.common.utils import log_trace, get_unique_name, try_times
from RuckusAutoTest.components import (
                                    create_fm_by_ip_addr,
                                    create_zd_by_ip_addr,
                                    clean_up_rat_env,
                               )
from RuckusAutoTest.components import Helper_ZD as zd
from RuckusAutoTest.components import Helper_FM9 as fm9

def _verify_create(cfg):
    ''''''
    msg = _monitor(
        cfg['fm'], cfg['prov_cfg']['task_name'], cfg['delta'], 'success'
    )
    if msg: return dict(result='ERROR', message=msg)

    msg = _verify_ui_result(
            cfg['fm'], cfg['zd'],
            cfg['tmpl_cfg']['tmpl_name'], cfg['tmpl_cfg']['cfg']
    )
    if msg:
        res = dict(result='ERROR', message=msg)
    else:
        res = dict(
            result  = 'PASS',
            message = 'The test "create" for "%s", schedule: "%s" works successfully' % \
                      (cfg['prov_to'], cfg['prov_cfg']['schedule'])
        )

    return res

def _verify_restart(cfg):
    ''''''
    _set_call_home_interval(cfg['zd'], False)

    # Wait the task expired
    msg = _monitor(
        cfg['fm'], cfg['prov_cfg']['task_name'], cfg['delta'], 'restartable'
    )
    if msg:
        return dict(result='ERROR', message= 'Cannot restart the task "Success"')

    _set_call_home_interval(cfg['zd'], True, cfg['fm_ip'])

    msg = _restart(cfg['fm'], cfg['prov_cfg']['task_name'])
    if msg: return dict(result='ERROR', message=msg)

    msg = _monitor(
        cfg['fm'], cfg['prov_cfg']['task_name'], cfg['delta'], 'success'
    )
    if msg: return dict(result='ERROR', message=msg)

    msg = _verify_ui_result(
        cfg['fm'], cfg['zd'],
        cfg['tmpl_cfg']['tmpl_name'], cfg['tmpl_cfg']['cfg']
    )
    if msg:
        res = dict(result='ERROR', message=msg)
    else:
        res = dict(result='PASS', message='The test "restart" works successfully')

    return res

def _verify_cancel(cfg):
    ''''''
    msg = _cancel(cfg['fm'], cfg['prov_cfg']['task_name'])
    if msg:
        res = dict(result='ERROR', message=msg)
    else:
        res = dict(result='PASS', message='The test "cancel" works successfully')

    return res

def _verify_delete(cfg):
    ''''''
    msg = _delete_task(cfg['fm'], cfg['prov_cfg']['task_name'])
    if msg:
        res = dict(result='ERROR', message=msg)
    else:
        res = dict(result='PASS', message='The test "cancel" works successfully')

    return res

#-------------------------------------------------------------------------------
def _obtain_zd_cfg(cfg):
    '''
    '''
    msg, retries = None, 4
    for i in try_times(retries, 15):
        try:
            fm9.zd_cfg.obtain_zd_cfg_by_ip(
                cfg['fm'], cfg['zd_ip'], cfg['bk_cfg']['cfg_desc']
            )
            logging.info(
                'Obtained ZD cfg. IP: %s. Cfg desc: %s' %
                (cfg['zd_ip'], cfg['bk_cfg']['cfg_desc'])
            )
            break
        except Exception, e:
            if i < retries:
                logging.info('Warning: Cannot get the zd cfg. Re-try again...')
                continue
            msg = 'Error while obtaining the ZD cfg. Error: %s' % e.__str__()

    return msg


def _create_tmpl(cfg):
    '''
    '''
    msg = None
    try:
        fm9.zd_tmpl.create_zd_tmpl(
            cfg['fm'], cfg['tmpl_cfg']['tmpl_name'],
            cfg['bk_cfg']['cfg_desc'], cfg['tmpl_cfg']['cfg']
        )
        logging.info(
            'Created the ZD cfg template %s successfully' % cfg['tmpl_cfg']['tmpl_name']
        )
    except Exception, e:
        log_trace()
        msg = 'Could not create the report. Error: %s' % e.__str__()

    return msg

def _create_task(cfg):
    msg = None
    # create a view if provision to a group
    if 'view' in cfg['prov_cfg']:
        fm9.idev.create_zd_view(
            cfg['fm'], cfg['view_cfg']['name'], cfg['view_cfg']['options']
        )

    try:
        cfg['delta'] = fm9.zd_cu.create_task(
            cfg['fm'], cfg['prov_cfg']
        )
        logging.info(
            'Created a new zd cfg task %s' % cfg['prov_cfg']['task_name']
        )
    except Exception, e:
        log_trace()
        msg = 'Cannot create a ZD configuration task. Error: %s' % e.__str__()

    return msg

def _monitor(fm, task_name, delta, expect_status = 'success'):
    ''''''
    msg = None
    check_fn = dict(
        success = fm9.zd_cu.is_success_status,
        restartable = fm9.zd_cu.is_restartable_status,
    )
    try:
        ts, dt = fm9.zd_cu.monitor_task(fm, task_name)
        if check_fn[expect_status](ts):
            logging.info(
                'Task %s is finished. (Status, Detail): (%s, %s)' %
                (task_name, ts, dt)
            )
        else:
            msg = 'Error. Expect: %s. Result: %s. Detail: %s' % \
                  (expect_status, ts, dt)
    except Exception, e:
        msg = 'Cannot monitor the task. Error: %s' % e.__str__()

    return msg

def _cancel(fm, task_name):
    msg = None
    try:
        ts, dt = fm9.zd_cu.cancel_task(fm, task_name, 15)
        if fm9.zd_cu.is_canceled_status(ts):
            logging.info(
                'Canceled task %s. (status, Detail): (%s, %s)' %
                (task_name, ts, dt)
            )
        else:
            msg = 'Error. Expect: Canceled. Result: %s. Detail: %s' % (ts, dt)
    except Exception, e:
        msg = 'Error occurs. Error: %s' % e.__str__()

    return msg

def _restart(fm, task_name):
    msg = None
    try:
        ts, dt = fm9.zd_cu.restart_task(fm, task_name)
        if fm9.zd_cu.is_success_status(ts):
            logging.info(
                'Restarted task %s successfully. (Status, Detail): (%s, %s)' %
                (task_name, ts, dt)
            )
        else:
            msg = 'Error. Expect: Success. Result: %s. Detail: %s' % (ts, dt)
    except Exception, e:
        msg = 'Cannot restart the task. Error: %s' % e.__str__()

    return msg

def _delete_task(fm, task_name):
    msg = None
    try:
        fm9.zd_cu.delete_task(fm, task_name)
        logging.info(
            'Delete task %s successfully!!!' % (task_name)
        )
    except Exception, e:
        msg = 'Cannot delete the task. Error: %s' % e.__str__()

    return msg

def _verify_ui_result(fm_obj, zd_obj, tmpl_name, tmpl_cfg):
    msg = None
    try:
        logging.info('Verifying the result...')

        # get cfg from ZD UI
        logging.info('Getting ZD UI cfg...')
        zd_cfg = _get_cfg_from_zd_ui(zd_obj, tmpl_cfg)

        # get cfg of ZD template from FM
        logging.info('Getting ZD template cfg...')
        tmpl_cfg = fm9.zd_tmpl.get_tmpl_cfg(fm_obj, tmpl_name)

        logging.info('ZD template cfg: %s' % pformat(tmpl_cfg))
        logging.info('ZD UI cfg: %s' % pformat(zd_cfg))

        if tmpl_cfg == zd_cfg:
            logging.info('Template and ZD UI cfg is them same')
        else:
            msg = 'Error: ZD template and ZD UI cfg is different'
    except Exception, e:
        log_trace()
        msg = 'Cannot verify UI result. Error: %s' % e.__str__()

    if msg: logging.info(msg)
    return msg

def _get_cfg_from_zd_ui(zd, tmpl_cfg):
    cfg = {}

    zd.logout()
    zd.login()
    for k in tmpl_cfg.keys():
        cfg[k] = fm9.zd_tmpl.get_form_cfg(zd, k, is_nav = True)

    return cfg

def _set_call_home_interval(zd_obj, enabled = True, fm_ip = '', interval = 2):
    ''''''
    msg = zd.sys.set_fm_mgmt_info(
        zd_obj, dict(enabled=enabled, url=fm_ip, interval=interval)
    )
    logging.info('Return: %s' % msg)
    time.sleep(10)
#------------------------------------------------------------------------------
#                            Sample config for ZD template
###############################################################################
zd_cfg = dict(
    wlans = dict(
        wlan = {
            'ssid': 'zd_tmpl_auto', 'description': 'test',
            'auth': 'open', # 'open' | 'shared' | 'eap' | 'mac'
            'wpa_ver': '',
            'encryption': 'none', ## 'none' | 'wpa' | 'wpa2' | 'wpa_mixed' | 'wep64' | 'wep128'
            #'type': 'standard', 'hotspot_profile': '',
            #'key_string': '', 'key_index': '', 'auth_svr': '',
            #'do_webauth': None, 'do_isolation': None, 'do_zero_it': None,
            #'do_dynamic_psk': None, 'acl_name': '', 'l3_l4_acl_name': '',
            #'uplink_rate_limit': '', 'downlink_rate_limit': '',
            #'dvlan': False, 'vlan_id': None, 'do_hide_ssid': None,
            #'do_tunnel': None, 'acct_svr': '', 'interim_update': None
        },
        wlan_group = dict(
            name = 'zd_tmpl_group',
            description = 'Automation test',
            wlan_member = ['zd_tmpl_auto'],
            vlan_override = True, #True | False,
        ),
        psk_expiration = 'One week', #'Unlimited' | 'One day' | 'One week' | 'Two weeks'...
    ),
    ap_policies = dict(
        limited_zd_discovery = dict(
            enabled = True, # False
            # Just for creating ZD template, no need exact ZD ip now
            primary_zd_ip = '192.168.30.251',
            secondary_zd_ip = '',
        ),
    ),
    hotspot_services = {
        'service':  {
            'name': 'zd_cfg_template_hotspot',
            'login_page': 'login.htm',
            'start_page': None,
            'session_timeout': 40,
            'idle_timeout': 10,
            'auth_svr': '', #'192.168.30.252',
            'acct_svr': '', #'192.168.30.252',
            #'interim_update_interval': None,
            #'radius_location_id': '',
            #'radius_location_name': '',
            #'walled_garden_list': [],
            #'restricted_subnet_list': [],
            #'enable_mac_auth': None,
        },
    },
    aaa_servers = dict(
        server = {
            'server_name': 'radius_srv',
            'server_addr': '192.168.30.252',
            'server_port': '1812',
            #'win_domain_name': '', 'ldap_search_base': '',
            #'ldap_admin_dn': '', 'ldap_admin_pwd': '',
            'radius_auth_secret': '123456',
            #'radius_acct_secret': ''
        }
    ),
    system = dict(
        log = dict(
            log_level = 'show_more', #'warning_and_critical' | 'critical_events_only'
            enable_remote_syslog = True, # False
            remote_syslog_ip = '192.168.30.252',
        )
    ),
)
#------------------------------------------------------------------------------

def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',
        zd_ip = '192.168.30.251',
        action = 'create', #'cancel', 'delete'
        prov_to = 'device', #'group'
        schedule = 0,
    )
    p.update(cfg)

    suffix = get_unique_name('')
    # Define config to obtain a ZD backup cfg
    p['bk_cfg'] = dict(
        cfg_desc = 'bk_cfg' + suffix,
    )
    # Define config to create a ZD template
    p['tmpl_cfg'] = dict(
        tmpl_name   = 'tmpl' + suffix,
        bk_cfg_name = p['bk_cfg']['cfg_desc'],
        cfg         = zd_cfg,
    )
    # Define config to do provision a zd task
    p['prov_cfg'] = dict(
        task_name = 'prov_cfg' + suffix,
        schedule  = p.pop('schedule'),
        cfg_type  = 'config',
        cfg_file  = p['tmpl_cfg']['tmpl_name']
    )
    if p['prov_to'] == 'device':
        p['prov_cfg']['device'] = [p['zd_ip']]
    else:
        p['prov_cfg']['view'] = 'group_' + p['zd_ip']
        p['view_cfg'] = dict(
            name = p['prov_cfg']['view'],
            options = [['IP Address', 'Contains', p['zd_ip']],]
        )
    # update the zd ip according to the user's input
    zd_cfg['ap_policies']['limited_zd_discovery']['primary_zd_ip'] = p['zd_ip']
    p['fm'] = create_fm_by_ip_addr(p['fm_ip'])
    p['zd'] = create_zd_by_ip_addr(p['zd_ip'])

    _set_call_home_interval(p['zd'], True, p['fm_ip'])

    logging.info('Remove all ZD config first')
    p['zd'].remove_all_cfg()

    logging.info('Test config: \n%s' % pformat(p))

    return p


def do_test(cfg):
    ''''''
    res = _obtain_zd_cfg(cfg)
    if res: return dict(result='ERROR', message = res)

    res = _create_tmpl(cfg)
    if res: return dict(result='ERROR', message = res)

    msg = _create_task(cfg)
    if msg: return dict(result='ERROR', message=msg)

    verify_fn = dict(
        create = _verify_create,
        restart = _verify_restart,
        cancel = _verify_cancel,
        delete = _verify_delete,
    )[cfg['action']]

    res = verify_fn(cfg)

    return res


def do_clean_up(cfg):
    try:
        logging.info('Cleaning up...')
        if cfg['action'] in ['create', 'restart']:
            cfg['zd'].remove_all_cfg()
            logging.info('Remove all ZD cfg')

        fm9.zd_cfg.delete_zd_cfg_by_desc(cfg['fm'], cfg['bk_cfg']['cfg_desc'])
        logging.info('Deleted the zd back up cfg %s' % cfg['bk_cfg']['cfg_desc'])

        fm9.zd_tmpl.delete_zd_tmpl(cfg['fm'], cfg['tmpl_cfg']['tmpl_name'])
        logging.info('Deleted the ZD template %s' % cfg['tmpl_cfg']['tmpl_name'])

        if cfg['action'] != 'delete':
            fm9.zd_cu.delete_task(cfg['fm'], cfg['prov_cfg']['task_name'])
            logging.info('Deleted the task %s' % cfg['prov_cfg']['task_name'])

        cfg['zd'].stop()
    except:
        log_trace()
        logging.info('Error occurs while cleaning up the test')

    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res


'''

'''
