'''
Support page:
    Configure > ZoneDirectors > Config Tasks.
Supported Functions:
1. Create:
    . Create a new task for Config mode w/wo schedule
    . Create a new task for Restore mode (cloning) w/wo schedule
        . Full restore.
        . Failover restore.
        . Policy restore.
2. Cancel:
    . to cancel a task
3. Delete:
    . to delete a task
4. Restart:
    . to restart a task
'''
from RuckusAutoTest.components.lib.fm import provisioning_fm as prov
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, \
       get as ac_get, cfg_data_flow

from RuckusAutoTest.components.lib import dev_features

#-------------------------------------------------------------------------------
#                        PUBLIC METHODs
def create_task(fm, cfg):
    '''
    . to support create a task for two mode "Configuration" and "Restore".
    . update 'schedule' and 'device' params accordingly
    . click create new task link
    . call set for provisioning
    cfg:
    1. Common keys:
        . task_name
        . device: a list of device IPs.
        . view: group name.
        . schedule: an int
    2. Specific keys for "config" mode:
        . cfg_type: "config"
        . cfg_file: ZD template name
    3. Specific keys for "restore" mode:
        . cfg_type: "restore"
        . cfg_file: ZD config backup name
        . restore_type: 'full' | 'failover' | 'policy'
    '''
    s, l = fm.selenium, locators
    delta = prov.update_cfg(cfg)

    nav_to(fm, force = True)
    s.click_and_wait(l['new_task_link'])
    set(fm, cfg, is_nav = False)
    s.click_and_wait(l['save_btn'])

    return delta

def monitor_task(fm, task_name, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.monitor_task(fm, dict(task_name=task_name), mcfg, timeout)

def cancel_task(fm, task_name, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.cancel_task(fm, dict(task_name=task_name), mcfg, timeout)

def restart_task(fm, task_name, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.restart_task(fm, dict(task_name=task_name), mcfg, timeout)

def delete_task(fm, task_name):
    return prov.delete_task(fm, dict(task_name=task_name), mcfg)

def is_restartable_status(ts):
    return prov.is_restartable_status(ts)

def is_success_status(ts):
    return prov.is_success_status(ts)

def is_canceled_status(ts):
    return prov.is_canceled_status(ts)

#-------------------------------------------------------------------------------
#                        UNPUBLIC METHODs
zd_cfg_tasks_loc = dict(
    cfg_type = Ctrl(
        loc = dict(
            config = "//input[@id='configtype.0']",
            restore = "//input[@id='configtype.1']"
        ),
        type = 'radioGroup',
    ),
    cfg_file = Ctrl(loc = "//select[@id='select-configlist']", type = 'select'),

    restore_type = Ctrl(
        loc = dict(
            full = "//input[@id='type.0']",
            failover = "//input[@id='type.1']",
            policy = "//input[@id='type.2']",
        ),
        type = 'radioGroup',
    ),
)

locators = prov.get_ctrls(dict())
locators.update(zd_cfg_tasks_loc)
locators['task_detail_tbl'].cfg['hdrs'] = dev_features.FM.reboot_task_detail_ths
ctrl_order = prov.get_order_ctrls([
    dict(enter = 'cfg_type', items = ['cfg_file'],)
])


def set(fm, cfg, is_nav = True):
    s, l, oc = fm.selenium, locators, cfg_data_flow(cfg, ctrl_order)
    if is_nav:
        nav_to(fm, force = True)
    ac_set(s, l, cfg, oc)


def get(fm, cfg, is_nav = True):
    '''
    for getting Task Status Details, set is_nav=False
    '''
    s, l, oc = fm.selenium, locators, cfg_data_flow(cfg, ctrl_order)
    if is_nav:
        nav_to(fm, force = True)
    return ac_get(s, l, cfg, oc)


#------------------------------------------------------------------------------
def nav_to(fm, force = False):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_ZD_CONFIG_TASKS, force = force)

m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = None, # don't use now
)

mcfg = dict(get = get, set = set, nav_to = nav_to,) # this module config funcs


#def _set(fm, cfg, order = 'default'):
#    return fns.set(m, fm, cfg, is_nav = False, order = order)

#def _get(fm, cfg, order = 'default'):
#    return fns.get(m, fm, cfg, is_nav = False, order = order)
