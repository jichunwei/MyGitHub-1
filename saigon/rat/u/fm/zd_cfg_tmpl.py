'''
#------------------------------------------------------------------------------
IMPORTANT:
This tea to support following functions in Configure > ZoneDirectors > Config Templates
 . create
 . edit
 . delete
#------------------------------------------------------------------------------

Examples to do other functions: query, edit, delete
tea.py u.fm.zd_cfg_tmpl fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=create
tea.py u.fm.zd_cfg_tmpl fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=edit
tea.py u.fm.zd_cfg_tmpl fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=delete
'''

import logging
from pprint import pformat
from RuckusAutoTest.common.utils import log_trace, get_unique_name
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components.lib.fm import zd_cfg_mgmt_fm as zd_cfg
from RuckusAutoTest.components.lib.fm9 import zd_cfg_tmpl as zd_tmpl

def _verify_create(cfg):
    ''''''
    res = zd_tmpl.find_zd_tmpl(cfg['fm'], cfg['tmpl_name'])
    logging.info('Found the ZD template %s' % cfg['tmpl_name'])
    return dict(result='PASS', message='Created the ZD template successfully') \
           if res else \
           dict(result='ERROR', message='Fail to create the ZD template.')


def _verify_edit(cfg):
    ''''''
    try:
        logging.info(
            'Change cfg of the template to cfg: %s' % pformat(cfg['zd_cfg_2'])
        )
        zd_tmpl.edit_zd_tmpl(cfg['fm'], cfg['tmpl_name'], cfg['zd_cfg_2'])
        return dict(
            result = 'PASS',
            message = 'Edited the ZD template successfully'
        )
    except Exception, e:
        return dict(
            result = 'ERROR',
            message = 'Fail to edit the ZD template. Error: %s' % e.__str__()
        )


def _verify_delete(cfg):
    ''''''
    try:
        zd_tmpl.delete_zd_tmpl(cfg['fm'], cfg['tmpl_name'])
        return dict(
            result = 'PASS',
            message = 'Deleted the ZD template successfully'
        )
    except Exception, e:
        return dict(
            result = 'ERROR',
            message = 'Fail to delete the ZD template. Error: %s' % e.__str__()
        )

#-------------------------------------------------------------------------------
def _obtain_zd_cfg(cfg):
    '''
    '''
    msg = None
    try:
        logging.info(
            'Obtain ZD cfg. IP: %s. Cfg desc: %s' %
            (cfg['zd_ip'], cfg['zd_cfg_desc'])
        )
        zd_cfg.obtain_zd_cfg_by_ip(cfg['fm'], cfg['zd_ip'], cfg['zd_cfg_desc'])
    except Exception, e:
        msg = 'Error while obtaining the ZD cfg. Error: %s' % e.__str__()

    return msg


def _create_zd_tmpl(cfg):
    '''
    '''
    msg = None
    try:
        zd_tmpl.create_zd_tmpl(
            cfg['fm'], cfg['tmpl_name'], cfg['zd_cfg_desc'], cfg['zd_cfg_1']
        )
        logging.info(
            'Created the ZD cfg template %s successfully' % cfg['tmpl_name']
        )
    except Exception, e:
        log_trace()
        msg = 'Could not create the report. Error: %s' % e.__str__()

    return msg

#------------------------------------------------------------------------------
#                            Sample config for ZD template
###############################################################################
zd_cfg_1 = dict(
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
            'service': {
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
    )

zd_cfg_2 = dict(
    aaa_servers = {
        'server': {
            'server_name': 'radius_srv',
            'server_addr': '192.168.30.252',
            'server_port': '1812',
            #'win_domain_name': '', 'ldap_search_base': '',
            #'ldap_admin_dn': '', 'ldap_admin_pwd': '',
            'radius_auth_secret': '123456',
            #'radius_acct_secret': ''
        },
    },
    system = dict(
        log = dict(
            log_level = 'show_more', #'warning_and_critical' | 'critical_events_only'
            enable_remote_syslog = True, # False
            remote_syslog_ip = '192.168.30.252',
        ),
    ),
)
#------------------------------------------------------------------------------

def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',
        zd_ip = '192.168.30.251',
        zd_cfg_desc = get_unique_name('zd_cfg'),
        tmpl_name = get_unique_name('zd_tmpl') ,
        action = 'create',
        zd_cfg_1 = zd_cfg_1,
    )
    p.update(cfg)

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip'))

    if p['action'] == 'edit':
        p['zd_cfg_2'] = zd_cfg_2

    logging.info('Test config: \n%s' % pformat(p))

    return p


def do_test(cfg):
    ''''''
    res = _obtain_zd_cfg(cfg)
    if res: return dict(result='ERROR', message = res)

    res = _create_zd_tmpl(cfg)
    if res: return dict(result='ERROR', message = res)

    test_fn = dict(
        create = _verify_create,
        edit = _verify_edit,
        delete = _verify_delete,
    )[cfg['action']]
    res = test_fn(cfg)

    return res


def do_clean_up(cfg):
    try:
        logging.info('Cleaning up...')

        zd_cfg.delete_zd_cfg_by_desc(cfg['fm'], cfg['zd_cfg_desc'])
        logging.info('Deleted the zd back up cfg %s' % cfg['zd_cfg_desc'])
        if cfg['action'] != 'delete':
            zd_tmpl.delete_zd_tmpl(cfg['fm'], cfg['tmpl_name'])
            logging.info('Deleted the ZD template %s' % cfg['tmpl_name'])
    except:
        logging.info('Error occurs while cleaning up the test')

    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res


'''

'''
