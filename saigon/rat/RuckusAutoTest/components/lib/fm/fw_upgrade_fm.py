'''
A note on input params
. model selection:
  . accepting zf2925_fw, zf7942_fw... and convert them to real ctrls by _fmt fn
'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.fm import provisioning_fm as prov
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, \
       get as ac_get, cfg_data_flow

# accepting many keys following this template '%s_fw' ie. zf2925_fw, zf7942_fw...
FW_TMPL = Ctrl("//table[@id='tbmodelfirmware']//tr[./td='%s']/td/select", type = 'select')

locators = prov.get_ctrls(dict(
    reboot = Ctrl("//input[@id='reboot.flag']", type = 'check'),
))

ctrl_order = prov.get_order_ctrls(['model_fw_tmpl', ])


def nav_to(fm, force = False):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_FIRMWARE_UPGRADE, force = force)


def _fmt(cfg_ks):
    '''
    . if this model not in ctrl, ctrl_order then:
      . look for all '%s_fw's on the keys then format controls with that arg
      . returning a loc dict with model_fw formatted as zf2925_fw, zf7942_fw...
      . keep the ctrl_k on ctrl_order for next insertion
    '''
    l, oc = locators, ctrl_order
    ctrl_k, ktmpl = 'model_fw_tmpl', '_fw'
    for k in cfg_ks:
        if k.endswith(ktmpl) and k not in l:
            l[k] = copy.deepcopy(FW_TMPL)
            l[k].loc %= k.split(ktmpl)[0].upper()
            oc.insert(oc.index(ctrl_k), k)
    return l, oc


def set(obj, cfg, is_nav = True):
    s = obj.selenium
    l, oc = _fmt(cfg.keys() if isinstance(cfg, dict) else cfg)
    oc = cfg_data_flow(cfg, oc)
    if is_nav:
        nav_to(obj, force = True)
    ac_set(s, l, cfg, oc)


def get(obj, cfg, is_nav = True):
    '''
    for getting Task Status Details, set is_nav=False
    '''
    s = obj.selenium
    l, oc = _fmt(cfg.keys() if isinstance(cfg, dict) else cfg)
    oc = cfg_data_flow(cfg, oc)
    if is_nav:
        nav_to(obj, force = True)
    return ac_get(s, l, cfg, oc)


def create_task(obj, cfg):
    '''
    TODO: update the how the fw selection here
    . update 'schedule' and 'device' params accordingly
    . click create new task link
    . call set for provisioning
    cfg
    . task_name
    . SPECIFICS
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

