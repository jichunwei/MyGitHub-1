from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.fm import provisioning_fm as prov
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, \
       get as ac_get, cfg_data_flow


locators = prov.get_ctrls(dict(
    reboot = Ctrl("//input[@id='reboot.flag']", type = 'check'),
))

ctrl_order = prov.get_order_ctrls(['reboot', ])


def nav_to(fm, force = False):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_FACTORY_RESET, force = force)


def set(obj, cfg, is_nav = True):
    s, l, oc = obj.selenium, locators, cfg_data_flow(cfg, ctrl_order)
    if is_nav:
        nav_to(obj, force = True)
    ac_set(s, l, cfg, oc)


def get(obj, cfg, is_nav = True):
    '''
    for getting Task Status Details, set is_nav=False
    '''
    s, l, oc = obj.selenium, locators, cfg_data_flow(cfg, ctrl_order)
    if is_nav:
        nav_to(obj, force = True)
    return ac_get(s, l, cfg, oc)


def create_task(obj, cfg):
    '''
    . update 'schedule' and 'device' params accordingly
    . click create new task link
    . call set for provisioning
    cfg
    . task_name
    . SPECIFICS: reboot
    . device: a list of device IPs
    . schedule: an int
    '''
    s, l = obj.selenium, locators
    delta = prov.update_cfg(cfg)

    nav_to(obj, force = True)
    s.click_and_wait(l['new_task_link'])
    set(obj, cfg, is_nav = False)
    s.click_and_wait(l['save_btn'])
    return delta


mcfg = dict(get = get, set = set, nav_to = nav_to,) # this module config funcs

def monitor_task(obj, cfg, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.monitor_task(obj, cfg, mcfg, timeout)


def cancel_task(obj, cfg, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.cancel_task(obj, cfg, mcfg, timeout)


def restart_task(obj, cfg, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.restart_task(obj, cfg, mcfg, timeout)

