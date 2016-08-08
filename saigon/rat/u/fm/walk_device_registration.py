'''
This is tea program for Device Registration
Examples:
tea.py u.fm.walk_device_registration fm_ip='192.168.0.124' ap_ip='192.168.0.236' status=permitted
tea.py u.fm.walk_device_registration fm_ip='192.168.0.124' ap_ip='192.168.0.236' status=admin_denied
tea.py u.fm.walk_device_registration fm_ip='192.168.0.124' ap_ip='192.168.0.236' status=rma
tea.py u.fm.walk_device_registration fm_ip='192.168.0.124' ap_ip='192.168.0.236' status=unavail
'''


import os
import logging
import time
from pprint import pformat

from RuckusAutoTest.common.utils import get_cfg_items
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.tests.fm.lib_FM import wait4_ap_up, get_ap_serial, reboot_ap
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.RuckusAP import RuckusAP

AP_LICENSE = 1
PERMITTED_ST = "permitted"
ADMIN_DENIED_ST = "admin_denied"
#"permitted", "admin_denied", "rma", "unavai"

STATUS_COMMENT = dict(
        permitted    = ('Permitted', 'AutoTest: Change to Permitted'),
        admin_denied = ('Admin Denied', 'AutoTest: Change to Admin Denied'),
        rma          = ('RMA', 'AutoTest: Change to RMA'),
        unavail       = ('Unavailable', 'AutoTest: Change to Unavailable'),
)

EXPECT_RESULT_ERR_MSG = dict(
    permitted = (True, 'Expect: Found device (ip, serial): (%s, %s) in Inventory but not found it'),
    admin_denied = (False, 'Expect: Not found device (ip, serial): (%s, %s) in Inventory but found it'),
    rma = (False, 'Expect: Not found device (ip, serial): (%s, %s) in Inventory but found it'),
    unavail = (False, 'Expect: Not found device (ip, serial): (%s, %s) in Inventory but found it'),
)

def _verify_permitted_status(cfg):
    '''
    '''

def _pre_config_status_test(cfg):
    '''
    This is to do pre-config for test cases "Verify AP status".
    If verify "permitted":
      1. Change it to "Admin Denied" first.
      2. delta_license = +1

    Other status:
      1. Change it to "permitted" first (just to make sure
      2. delta_license = -1

    Return:
      Return delta_license
    '''
    if cfg['status'] == PERMITTED_ST:
        logging.info('Do preconfig for the test: %s' % cfg['status'])
        status, comment = STATUS_COMMENT[ADMIN_DENIED_ST]
        cfg['fm'].lib.dreg.set_device_status(cfg['fm'], cfg['serial'], status, comment)


def _change_ap_to_test_status(cfg):
    ''''''
    # get license before change to test status
    cfg['license_before_change_status'] = cfg['fm'].lib.dreg.get_licenses_info(cfg['fm'])['licenses_for_ap']

    status, comment = STATUS_COMMENT[cfg['status']]
    cfg['fm'].lib.dreg.set_device_status(cfg['fm'], cfg['serial'], status, comment)
    if cfg['status'] == PERMITTED_ST:
        _reboot_and_wait_4_ap_up(cfg['ap_ip'])


def _check_ap_on_inventory_page(cfg):
    '''
    Check to make sure device is shown/not shown on Inventory Device page as expect
    '''
    # 1. Check to make found/not found as expect status
    data, row = cfg['fm'].lib.idev.find_device_serial(cfg['fm'], cfg['serial'])
    cur_status = (data!=None)
    expect_status, msg = EXPECT_RESULT_ERR_MSG[cfg['status']]

    err_msg = None
    if cur_status != expect_status:
        err_msg = msg % (cfg['ap_ip'], cfg['serial'])
        logging.info(err_msg)

    return err_msg


def _check_license_update(cfg):
    '''
    Check to make sure FM update license info after change status
    '''
    delta_license = AP_LICENSE if cfg['status'] == PERMITTED_ST else -AP_LICENSE
    cfg['license_after_change_status'] = cfg['fm'].lib.dreg.get_licenses_info(cfg['fm'])['licenses_for_ap']

    err_msg = None
    if int(cfg['license_after_change_status']) != (int(cfg['license_before_change_status']) + delta_license):
        err_msg = ('FM does not udpate license info. Expect: %s. Acutal: %s' %
            ((int(cfg['license_before_change_status']) + delta_license), int(cfg['license_after_change_status'])))
        logging.info(err_msg)
        return err_msg

    return err_msg


def _reboot_and_wait_4_ap_up(ip):
    '''
    '''
    cfg = dict(ip_addr = ip)
    reboot_ap(cfg)
    #config = dict(config=cfg)
    wait4_ap_up(**dict(config=cfg))
    # sometime ap up but still not appear in Manage Device page
    time.sleep(30)


def _get_serial(ap_ip):
    '''
    '''
    ap_cli = RuckusAP(dict(ip_addr = ap_ip))
    return ap_cli.get_serial()


def verify_inventory_status(cfg):
    '''
    Verify aps status.
    Required params:
     + serial: device serial
     + status: "permitted", "admin_denied", "rma", "unavai"
    '''
    map_status, comment = STATUS_COMMENT[cfg['status']]
    logging.info('Verify status %s for device serial %s' % (map_status, comment))

    cfg['serial'] = _get_serial(cfg['ap_ip'])
    _pre_config_status_test(cfg)

    _change_ap_to_test_status(cfg)
    err_msg =_check_ap_on_inventory_page(cfg)
    if err_msg: return dict(result='ERROR', message=err_msg)

    # 2. Check license after chagne to expect status.
    err_msg =_check_license_update(cfg)
    if err_msg: return dict(result='ERROR', message=err_msg)

    return dict(result='PASS',
                message='The test for satus "%s" works as expect' % cfg['status'])


def _clean_up_inventory_status_check(cfg):
    '''
    '''
    status, comment = STATUS_COMMENT[PERMITTED_ST]
    cfg['fm'].lib.dreg.set_device_status(cfg['fm'], cfg['serial'], status, comment)


def verify_upload_manufac_data_file(cfg):
    '''
    No need tea for this now.
    '''
    pass


def verify_upload_manufac_data_file_twice(cfg):
    '''
    No need tea for this now.
    '''
    pass


def verify_upload_prereg_data_file_twice(cfg):
    '''
    No need tea for this now.
    '''
    pass


def verify_save_inventory_file(cfg):
    '''
    No need tea for this now.
    '''
    pass


def do_config(cfg):
    p = dict(
        fm_ip  = '192.168.20.252',
        action = 'inventory_status',
        status = 'permitted',
    )
    p.update(cfg)
    p['fm'] = create_fm_by_ip_addr(cfg.pop('fm_ip'), version=cfg['version'])

    return p


def do_test(cfg):
    res = dict(
        inventory_status = verify_inventory_status,
        upload_manufac_data_file = verify_upload_manufac_data_file,
        upload_manufac_data_file_twice = verify_upload_manufac_data_file_twice,
        upload_prereg_data_file_twice = verify_upload_prereg_data_file_twice,
        save_inventory_file = verify_save_inventory_file,
    )[cfg['action']](cfg)

    return res


def do_clean_up(cfg):
    _clean_up_inventory_status_check(cfg)
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
