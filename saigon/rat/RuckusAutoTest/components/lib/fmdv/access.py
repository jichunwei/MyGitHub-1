from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, get as ac_get
from RuckusAutoTest.components.lib.fm import config_mapper_fm_old as cfgMapper
from RuckusAutoTest.components.lib import dev_features

Locators = dict(
    refresh_btn = "//img[contains(@title, 'Refresh')]",
    edit_btn = "//div[div='Edit Settings']",

    telnet_enabled = Ctrl(
        dict(enabled = "//input[contains(@id, 'radio_telnet_e')]",
             disabled = "//input[contains(@id, 'radio_telnet_d')]",
        ), type = 'radioGroup'),

    telnet_port = Ctrl("//input[contains(@id, 'input_telnet')]"),

    ssh_enabled = Ctrl(
        dict(enabled = "//input[contains(@id, 'radio_ssh_e')]",
             disabled = "//input[contains(@id, 'radio_ssh_d')]",
        ), type = 'radioGroup'),

    ssh_port = Ctrl("//input[contains(@id, 'input_ssh')]"),

    http_enabled = Ctrl(
        dict(enabled = "//input[contains(@id, 'radio_http_e')]",
             disabled = "//input[contains(@id, 'radio_http_d')]",
        ), type = 'radioGroup'),

    http_port = Ctrl("//input[contains(@id, 'input_http')][not(contains(@id, 'input_https'))]"),

    https_enabled = Ctrl(
        dict(enabled = "//input[contains(@id, 'radio_https_e')]",
             disabled = "//input[contains(@id, 'radio_https_d')]",
        ), type = 'radioGroup'),

    https_port = Ctrl("//input[contains(@id, 'input_https')]",),

    log_enabled = Ctrl(
        dict(enabled = "//input[contains(@id, 'radio_log_e')]",
             disabled = "//input[contains(@id, 'radio_log_d')]",
        ), type = 'radioGroup'),

    log_ip = Ctrl(
        ("//input[contains(@id, 'input_logaddr_1')]",
         "//input[contains(@id, 'input_logaddr_2')]",
         "//input[contains(@id, 'input_logaddr_3')]",
         "//input[contains(@id, 'input_logaddr_4')]",
        ), type = 'ipGroup'),

    log_port = Ctrl("//tr[contains(.,'port')]/td/input[contains(@id, 'input_log')]"),

    remote_mode = Ctrl(
        dict(auto = "//input[contains(@id, 'radio_rmm_auto')]",
             fm = "//input[contains(@id, 'radio_rmm_tr069')]",
             snmp = "//input[contains(@id, 'radio_rmm_snmp')]",
        ), type = 'radioGroup'),

    back_btn = "//div[div='Back']",
    submit_btn = "//div[div='submit' or div='Submit']",
    reset_btn = "//div[div='Reset']",
    task_id = "//div[contains(@class, 'displayDiv')]//*[contains(tr, 'Task #') or contains(tr, 'task #')]",
)

OrderedCtrls = ('telnet_enabled', 'ssh_enabled', 'http_enabled',
                'https_enabled', 'log_enabled')


def nav_to(obj, force = False):
    obj.navigate_to(obj.DETAILS, obj.DETAILS_MGMT, force = force)


def get(obj, cfg_ks):
    s, l = obj.selenium, Locators
    nav_to(obj)
    s.click_and_wait(l['refresh_btn'])
    s.click_and_wait(l['edit_btn'], 1)

    cfg = ac_get(s, l, cfg_ks)
    nav_to(obj, force = True)
    return cfg


def set(obj, cfg):
    s, l, oc = obj.selenium, Locators, OrderedCtrls
    nav_to(obj, force = True)
    s.click_and_wait(l['refresh_btn'])
    s.click_and_wait(l['edit_btn'], 1)

    ac_set(s, l, cfg, oc)

    s.click_and_wait(l['submit_btn'], 2)
    # locator of task id of this page different from other page so pass
    # the locator for get_task_status2
    return obj.get_task_status2(obj.get_task_id(l['task_id']))


def reset(obj, cfg_ks):
    s, d = obj.selenium, obj.access_mgmt
    return set(obj, dict([(k, d[k]) for k in cfg_ks]))

