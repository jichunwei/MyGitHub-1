'''
#------------------------------------------------------------------------------
IMPORTANT:
This tea to support following functions in Configure > ZoneDirectors > Config Templates
 . create
 . edit
 . delete
#------------------------------------------------------------------------------

Examples to do other functions: query, edit, delete
tea.py u.fm.zd_event_cfg fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=create
tea.py u.fm.zd_event_cfg fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=edit
tea.py u.fm.zd_event_cfg fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=copy
tea.py u.fm.zd_event_cfg fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=delete
tea.py u.fm.zd_event_cfg fm_ip=192.168.30.252 zd_ip=192.168.30.251 action=assign_zd
'''

import logging
from copy import deepcopy
from pprint import pformat
from RuckusAutoTest.common.utils import (
                                    log_trace,
                                    get_unique_name,
                                    compare_dict
                                 )
from RuckusAutoTest.components import (
                                    create_fm_by_ip_addr,
                                    clean_up_rat_env,
                               )
from RuckusAutoTest.components import Helper_FM9 as fm9

def _verify_create(cfg):
    ''''''
    msg = _find_event_cfg_tmpl(cfg['fm'], cfg['cfg_name_1'])
    if msg: return dict(result='ERROR', message=msg)

    ui_cfg = _get_result(cfg['fm'], cfg['cfg_name_1'], cfg['cfg_1'])
    msg = compare_dict(cfg['cfg_1'], ui_cfg)
    if msg:
        logging.info('Configure and UI keys are different. %s' % pformat(msg))
        res = dict(result='ERROR', message=msg)
    else:
        logging.info('Configure and UI keys are the same')
        res = dict(
            result  = 'PASS',
            message = 'The test "create" event cfg works successfully'
        )

    return res

def _verify_assign_event_cfg_to_zd(cfg):
    ''''''
    msg = None

    msg = _assign_event_cfg_to_zd(cfg)
    if msg: return dict(result='ERROR', message=msg)

    try:
        ip = fm9.zd_ec.get_configured_zd_ip_by_cfg_name(
                                            cfg['fm'], cfg['cfg_name_1'], cfg['view']
        )
        if ip != cfg['zd_ip']:
            msg = 'Expect: (%s, %s). Actual: (%s, %s)' % \
                  (cfg['zd_ip'], cfg['cfg_name_1'], ip, cfg['cfg_name_1'])
    except Exception, e:
        msg = 'Cannot get zd ip by cfg name. Error: %s' % e.__str__()

    if msg:
        res = dict(result = 'ERROR', message = msg)
    else:
        res = dict(
            result  = 'PASS',
            message = 'The test "assign_zd" works successfully'
        )

    return res

def _verify_edit(cfg):
    ''''''
    msg = _edit_event_cfg_tmpl(cfg)
    if msg: return dict(result='ERROR', message=msg)

    msg = _find_event_cfg_tmpl(cfg['fm'], cfg['cfg_name_1'])
    if msg: return dict(result='ERROR', message=msg)

    ui_cfg = _get_result(cfg['fm'], cfg['cfg_name_1'], cfg['cfg_2'])
    msg = compare_dict(cfg['cfg_2'], ui_cfg)
    if msg:
        res = dict(result='ERROR', message=msg)
    else:
        res = dict(
            result  = 'PASS',
            message = 'The test "edit" event cfg works successfully'
        )

    return res


def _verify_copy(cfg):
    ''''''
    msg = _copy_event_cfg_tmpl(cfg)
    if msg: return dict(result='ERROR', message=msg)

    msg = _find_event_cfg_tmpl(cfg['fm'], cfg['cfg_name_2'])
    if msg: return dict(result='ERROR', message=msg)

    ui_cfg = _get_result(cfg['fm'], cfg['cfg_name_1'], cfg['cfg_1'])
    msg = compare_dict(cfg['cfg_1'], ui_cfg)
    if msg:
        res = dict(result='ERROR', message=msg)
    else:
        res = dict(
            result  = 'PASS',
            message = 'The test "copy" event cfg works successfully'
        )

    return res

def _verify_delete(cfg):
    ''''''
    msg = _delete_event_cfg_tmpl(cfg)
    if msg: return dict(result='ERROR', message=msg)

    msg = _find_event_cfg_tmpl(cfg['fm'], cfg['cfg_name_1'])
    if not msg:
        res = dict(
            result = 'ERROR',
            message = 'The event cfg %s has not been removed yet' % cfg['cfg_name_1']
        )
    else:
        res = dict(
            result  = 'PASS',
            message = 'The test "delete" event cfg works successfully'
        )

    return res

def _create_event_cfg_tmpl(cfg):
    ''''''
    msg = None
    try:
        fm9.zd_ec.create_event_cfg(cfg['fm'], cfg['cfg_name_1'], cfg['cfg_1'])
        logging.info(
            'Created the ZD event cfg template %s successfully' % cfg['cfg_name_1']
        )
    except Exception, e:
        log_trace()
        msg = 'Cannot create the event cfg. Error: %s' % e.__str__()

    return msg


def _edit_event_cfg_tmpl(cfg):
    msg = None
    try:
        fm9.zd_ec.edit_event_cfg(cfg['fm'], cfg['cfg_name_1'], cfg['cfg_2'])
        logging.info(
            'Edited the ZD event cfg template %s successfully' % cfg['cfg_name_1']
        )
    except Exception, e:
        log_trace()
        msg = 'Cannot edit the event cfg. Error: %s' % e.__str__()

    return msg


def _copy_event_cfg_tmpl(cfg):
    msg = None
    try:
        fm9.zd_ec.copy_event_cfg(cfg['fm'], cfg['cfg_name_1'], cfg['cfg_name_2'])
        logging.info(
            'Copied the ZD event cfg to the new name: %s' % cfg['cfg_name_2']
        )
    except Exception, e:
        log_trace()
        msg = 'Cannot copy the event cfg. Error: %s' % e.__str__()

    return msg


def _delete_event_cfg_tmpl(cfg):
    msg = None
    try:
        fm9.zd_ec.delete_event_cfg(cfg['fm'], cfg['cfg_name_1'])
        logging.info(
            'Deleted the ZD event cfg %s' % cfg['cfg_name_1']
        )
    except Exception, e:
        log_trace()
        msg = 'Cannot delete the event cfg. Error: %s' % e.__str__()

    return msg


def _assign_event_cfg_to_zd(cfg):
    msg = None
    try:
        fm9.zd_ec.assign_zds(
            cfg['fm'], cfg['cfg_name_1'], [cfg['zd_ip']], cfg['view']
        )
        logging.info(
            'Assigned the ZD event cfg %s to zd %s' %
            (cfg['cfg_name_1'], cfg['zd_ip'])
        )
    except Exception, e:
        log_trace()
        msg = 'Cannot assign the event cfg to ZD. Error: %s' % e.__str__()

    return msg


def _get_result(fm, cfg_name, cfg):
    '''
    . cfg_name: event cfg name template to get the result
    . cfg: cfg dict to create event cfg.
    '''
    cfg_ks = {}
    for sub_t, sub_cfg in cfg.items():
        cfg_ks[sub_t] = sub_cfg.keys()

    return fm9.zd_ec.get_event_cfg_tmpl(fm, cfg_name, cfg_ks)


def _find_event_cfg_tmpl(fm, cfg_name):
    msg = None
    try:
        r = fm9.zd_ec.find_event_cfg_tmpl(fm, cfg_name)
        if r:
            logging.info('Found the ZD event cfg %s' % cfg_name)
        else:
            msg = 'Not found the ZD event cfg %s' % cfg_name
    except Exception, e:
        log_trace()
        msg = 'Cannot find the event cfg %s. Error: %s' % (cfg_name, e.__str__())

    return msg


def _check_configured_match(fm, cfg_name, view):
    msg = None
    try:
        ip = fm9.zd_ec.get_configured_zd_ip_by_cfg_name(fm, cfg_name, view)

        logging.info('Found the ZD %s configured by event cfg %s' % (ip, cfg_name))
    except Exception, e:
        log_trace()
        msg = 'Cannot find the event cfg %s. Error: %s' % (cfg_name, e.__str__())

    return msg


def _build_cfg_keys():
    '''
    . to build two cfg keys
    . return cfg1 with full keys and cfg2 to do edit.
    '''
    cfg1, cfg2 = {}, {}
    cfg_ks = fm9.zd_ec.build_cfg_event_keys(False)

    for item, ks in cfg_ks.items():
        cfg1[item] = dict.fromkeys(ks, True)

    cfg2 = deepcopy(cfg1)
    # delete one key to make two cfg different
    del cfg2['sys_admin']

    return cfg1, cfg2
#------------------------------------------------------------------------------

def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',
        zd_ip = '192.168.30.251',
        action = 'create', #'cancel', 'delete'
        view = 'All ZoneDirectors',
    )
    p.update(cfg)
    suffix = get_unique_name('')

    p['cfg_name_1'] = 'event_cfg' + suffix
    p['cfg_1'], p['cfg_2'] = _build_cfg_keys()


    if p['action'] == 'copy':
        p['cfg_name_2'] = 'event_cfg_2' + suffix

    p['fm'] = create_fm_by_ip_addr(p['fm_ip'])

    logging.info('Test config: \n%s' % pformat(p))

    return p


def do_test(cfg):
    ''''''
    res = _create_event_cfg_tmpl(cfg)
    if res: return dict(result='ERROR', message = res)


    verify_fn = dict(
        create    = _verify_create,
        assign_zd = _verify_assign_event_cfg_to_zd,
        copy      = _verify_copy,
        edit      = _verify_edit,
        delete    = _verify_delete,
    )[cfg['action']]

    res = verify_fn(cfg)

    return res


def do_clean_up(cfg):
    try:
        logging.info('Cleaning up...')

        if cfg['action'] not in ['delete','assign_zd']:
            fm9.zd_ec.delete_event_cfg(cfg['fm'], cfg['cfg_name_1'])
            logging.info('Deleted the event cfg %s' % cfg['cfg_name_1'])

        if cfg['action'] == 'copy':
            fm9.zd_ec.delete_event_cfg(cfg['fm'], cfg['cfg_name_2'])
            logging.info('Deleted the event cfg %s' % cfg['cfg_name_2'])

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
