from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, get as ac_get


Locators = dict(
    device_name = Ctrl(loc = "//input[@id='devicename']", type = 'text'),
    temp_update_interval = Ctrl(loc = "//input[@id='thermo']", type = 'text'),
    submit_btn = Ctrl(loc = "//input[@id='submit-button'][contains(@value,'Update')]", type = 'button'),
)

OrderedCtrls = ['device_name', 'temp_update_interval', 'submit_btn']


def nav_to(obj, force = False):
    return obj.navigate_to(obj.MAIN_PAGE, obj.CONFIG_DEVICE, force = force)


def set(obj, cfg):
    s, l, oc = obj.selenium, Locators, OrderedCtrls
    nav_to(obj)
    ac_set(s, l, cfg, oc)
    s.wait_for_page_to_load()


def get(obj, cfg_ks):
    s, l = obj.selenium, Locators
    nav_to(obj, force = True) # removing side effect
    cfg = ac_get(s, l, cfg_ks)
    return cfg


def reset(obj, cfg_ks):
    s, d = obj.selenium, obj.device
    return set(obj, dict([(k, d[k]) for k in cfg_ks]))

