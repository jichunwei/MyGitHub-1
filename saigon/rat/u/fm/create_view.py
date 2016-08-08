'''
create a view on saigon FM
. device_type: one of these: ap, zd, client

tea.py u.fm.create_view fm_ip_addr=192.168.0.245 view_name=ruckus_view device_type="ap" options="[['AP Name', 'Contains', 'att'], ['Serial Number', 'Ends with', '2210']]"
'''


import logging
from pprint import pformat

from RuckusAutoTest.common.utils import dict_by_keys
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env


def do_config(cfg):
    p = dict(
        fm_ip_addr = '192.168.20.252',
        view_name = 'ruckus_view',
        device_type = 'ap',
        options = [['AP Name', 'Contains', 'ruckus'],],
    )
    p.update(cfg)

    if p['device_type'] not in ['ap', 'zd', 'client']:
        raise Exception('Un-accepted device_type %s' % p['device_type'])

    p['fm'] = create_fm_by_ip_addr(p.pop('fm_ip_addr'), version='9')
    return p


def do_test(cfg):
    logging.info('Create a view [%s]' % cfg['view_name'])
    logging.debug('\n%s' % pformat(cfg))

    # first create the view
    # then go to that view and get all devices, print them out
    if cfg['device_type'] == 'ap':
        cfg['fm'].lib.idev.create_ap_view(
            **dict_by_keys(cfg, ['fm', 'view_name', 'options'])
        )

        cfg['fm'].lib.idev.get_all_aps_by_view_name(cfg['fm'], cfg['view_name'])
    elif cfg['device_type'] == 'zd':
        cfg['fm'].lib.idev.create_zd_view(
            **dict_by_keys(cfg, ['fm', 'view_name', 'options'])
        )

        cfg['fm'].lib.idev.get_all_zds_by_view_name(cfg['fm'], cfg['view_name'])
    else:
        cfg['fm'].lib.idev.create_client_view(
            **dict_by_keys(cfg, ['fm', 'view_name', 'options'])
        )

        cfg['fm'].lib.idev.get_all_clients_by_view_name(cfg['fm'], cfg['view_name'])
    return dict(result='PASS', message='View [%s] is created' % cfg['view_name'])


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
