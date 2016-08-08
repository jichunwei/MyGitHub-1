'''
Do some action related to firmware upgrade (create/cancel/restart firmware upgrade task)
    + Create firmware upgrade task:
        + Get all firmware files in Configure > Manage Firmware Files
        + User choose which firmware that he/she wants to upgrade/downgrade
        + Go to Configure > Firmware Upgrade
        + Click on "Create new task" link
        + Click on tab "Select devices"
        + Specify task name, device want to test and schedule time for the task
            Schedule time = 0 also means start the task now.
        + Click save to start the task
        + Monitor the task until have the result of the task.

    + Cancel schedule firmware upgrade task:
        + Go to Configure > Upgrade Firmware
        + Click on "cancel" link to cancel a schedule task.

    + Restart fail/expired firmware upgrade task:
        + Go to Configure > Upgrade Firmware
        + Click on "restart" link to restart fail/expired task.

    Things need to enhance:
        + Create lib to delete task
        + Cancel firmware upgrade task can be restart (now, we don't support this)

Examples:
tea.py u.fm.firmware_upgrade fm_ip_addr=97.74.124.173 fm_version='9' action=create_task task_name=firmware_upgrade device=['192.168.20.171'] schedule=0 model='ZF7942'
tea.py u.fm.firmware_upgrade fm_ip_addr=97.74.124.173 fm_version='9' action=cancel_task task_name=firmware_upgrade
tea.py u.fm.firmware_upgrade fm_ip_addr=97.74.124.173 fm_version='9' action=restart_task task_name=firmware_upgrade
'''


import os
import logging
import time
from pprint import pformat

#from RuckusAutoTest.common.utils import get_cfg_items
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env, _create_fm
from RuckusAutoTest.scripts.fm import libFM_TestSuite as lib_fm_ts
from RuckusAutoTest.common import utils
from RuckusAutoTest.components import Helpers as lib

def create_new_group(cfg):
    fm = cfg['fm']
    inven_cfg = cfg['inven_cfg']
    fm.create_model_group(**inven_cfg)

def get_upgrade_fw(tcfg):
    config = dict(model = 'ZF7942')
    config.update(tcfg)

    fws = dict(fs=utils.get_fws_on_local_file_system())
    fws['fm'] = [fw['firmwarename'] for fw in lib.fm.fw.get_all_firmwares(config['fm'])]
    # clean up what have been uploaded to FM from FileSystem list
    fws['fs'] = [i for i in fws['fs'] if not i in fws['fm']]
    upgrade_fw = lib_fm_ts.input_builds(models=[config['model']], localFws=fws)

    return upgrade_fw[config['model']][1][5:]


def create_upgrade_task(tcfg):
    tcfg['firmware'] = get_upgrade_fw(tcfg)

    lib.fm.fwup.create_task(tcfg['fm'], dict(task_name = tcfg['task_name'],
                                             schedule = tcfg['schedule'],
                                             device = tcfg['device']))
    print 'Monitor the task until it finish\n'
    return monitor_upgrade_task(tcfg)

def monitor_upgrade_task(tcfg):
    return lib.fm.fwup.monitor_task(tcfg['fm'], dict(task_name = tcfg['task_name'],))

def cancel_schedule_task(tcfg):
    return lib.fm.fwup.cancel_task(tcfg['fm'], dict(task_name = tcfg['task_name'],))

def restart_task(tcfg):
    return lib.fm.fwup.restart_task(tcfg['fm'], dict(task_name = tcfg['task_name'],))


def do_config(tcfg):
    config = dict(
        fm_ip_addr = '192.168.30.252',
        model = 'ZF7942',
        fm_version = '8',
        task_name = 'test_firmware_upgrade',
        schedule = 0,
        device=['192.168.20.171'],
        action = 'create_task'
    )
    config.update(tcfg)

    # in report case, we don't need FM
    config['fm'] = create_fm_by_ip_addr(ip_addr = config.pop('fm_ip_addr'),
                                        version = config.pop('fm_version'))

    return config


def do_test(cfg):
    return {'create_task' : create_upgrade_task,
            'cancel_task' : cancel_schedule_task,
            'restart_task' : restart_task}[cfg['action']](cfg)


def do_clean_up(cfg):
    clean_up_rat_env()

def main(**kwa):
    tcfg = do_config(kwa)
    result = do_test(tcfg)
    do_clean_up(tcfg)

    return result
