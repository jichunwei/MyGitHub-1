import logging
import time
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import * # rarely reloading, so import *
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import map_cfg_value

# %s = 0 to 7
# 0 --> Wireless 1
# 1 --> Wireless 2
# 2 --> Wireless 3
# ..............
# 7 --> Wireless 8
TabTmpl = "//div[@dojoinsertionindex='%s']"

Locators = dict(
    edit_btn = TabTmpl + "//div[@class='dojoButton' and div='Edit Settings']",
    back_btn = TabTmpl + "//div[@class='dojoButton' and div='Back']",
    submit_btn = TabTmpl + "//div[@class='dojoButton' and div='Submit']",
    reset_btn = TabTmpl + "//div[@class='dojoButton' and div='Reset']",
    downlink = Ctrl(TabTmpl + "//select[contains(@name, 'RateDown')]",
                    type = 'select'),
    uplink = Ctrl(TabTmpl + "//select[contains(@name, 'RateUp')]", type = 'select'),
    tab_link_tmpl = TabTmpl + "//span[1]",
)

def _nav_to(dv, wlan = 0, force = True):
    '''
    - wlan: from 0 to 7
        0 -> Wireless 1
        1 -> Wireless 2
        ...............
        7 -> Wireless 8
    '''
    dv.navigate_to(dv.DETAILS, dv.DETAILS_RATE_LIMITING, force = force)
    dv.selenium.click_and_wait(Locators['tab_link_tmpl'] % wlan)

def _get_locs(wlan = 0):
    '''
    This function is to map locator of Rate Limiting WLAN items
    wlan:
        0: Wireless 1,
        1: Wireless 2,
        ...
        7: Wireless 8,
    output:
    - return locator for wlan n
    '''
    return formatCtrl(Locators, [wlan])

def get_cfg(dv, wlan = 1, cfg_keys = []):
    '''
    This fucntion is to get items having keys provided in cfg_keys. if cfg_keys is empty,
    it gets all times
    Input:
    - dv: Device View instance
    - wlan: wlan to get its items. Value to pass for this param is from 1 to 8
    - cfg_keys: a list, keys of items to get
    Output:
    - return a dictionary of items
    '''
    logging.info('Get Rate Limiting items of %s config' % wlan)
    s, l = dv.selenium, _get_locs(wlan - 1)

    _nav_to(dv, wlan - 1, True)
    s.click_and_wait(l['edit_btn'])
    cfg = get(s, l, cfg_keys if cfg_keys else ['uplink', 'downlink'])

    return map_cfg_value(cfg, False)

def set_cfg(dv, wlan, cfg):
    '''
    This function is to set cfg for Rate Limiting of a wlan.
    Input:
    - dv: Device View instance,
    - wlan: wlan to set cfg.
    - cfg: a dictionary of configuration to set
    Output:
    - Return (task status, message)
    '''
    logging.info('Set Rate Limiting for wlan %s. Cfg: %s' % (wlan, pformat(cfg)))
    s, l = dv.selenium, _get_locs(wlan - 1)

    _nav_to(dv, wlan - 1, True)
    s.click_and_wait(l['edit_btn'])
    set(s, l, map_cfg_value(cfg))
    s.click_and_wait(l['submit_btn'])

    return dv.get_task_status(dv.get_task_id())

