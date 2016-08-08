from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, cfg_data_flow2
from RuckusAutoTest.components.lib.fm import config_mapper_fm_old as cm


#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def set_device_name(dv, name):
    return set(dv, dict(device_name=name))


def get_device_name(dv):
    return get(dv, dict(device_name=None))['device_name']


#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
CTRL_TMPL = "//td[contains(preceding-sibling::th, '%s')]/%s"
locators = dict(
    refresh_btn=Ctrl("//img[@title='Refresh']", 'button'),
    edit_btn=Ctrl("//div[@class='dojoButton' and div='Edit Settings']", 'button'),
    submit_btn=Ctrl("//div[@class='dojoButton' and div='Submit']", 'button'),

    tbl="//table[@class='displayDiv']",

    device_name = Ctrl(CTRL_TMPL % ('Device Name', 'input')),
    inform_interval = Ctrl(
        CTRL_TMPL % ('Periodic Inform Interval', 'select'),
        type = 'select'
    ),
    server_url = Ctrl(CTRL_TMPL % ('Server URL', 'input')),
    login_name = Ctrl(CTRL_TMPL % ('Login Name', 'input')),
    login_password = Ctrl(
        CTRL_TMPL % ('Login Password', "input[@type='password']")
    ),
    login_password2 = Ctrl(
        CTRL_TMPL % ('Password Confirmation', "input[@type='password']")
    ),

    # WARNING:
    # below ctrls have been removed from AP with version from 8.2.0.x
    monitoring_mode = Ctrl(CTRL_TMPL % ('Monitoring Mode', 'select'), type = 'select'),
    monitoring_interval = Ctrl(
        CTRL_TMPL % ('Monitoring Interval', "input[@id='associateIntervalValue']")
    ),
    monitoring_interval_unit = Ctrl(
        CTRL_TMPL % ('Monitoring Interval', 'select'), type = 'select'
    ),
)


_co = '''
  device_name inform_interval server_url login_name login_password login_password2
  monitoring_mode monitoring_interval monitoring_interval_unit
'''

ctrl_order = '[edit_btn %s submit_btn]' % _co # default one
get_co = '[edit_btn %s refresh_btn]' % _co


def nav_to(obj, force = False):
    return obj.navigate_to(obj.DETAILS, obj.DETAILS_DEVICE, force = force)


def set(obj, cfg):
    nav_to(obj, force = True)
    ac.set(obj.selenium, locators, cm.map_cfg_value(cfg),
           cfg_data_flow2(cfg.keys(), ctrl_order))
    return obj.get_task_status2(obj.get_task_id())


def get(obj, cfg_ks):
    nav_to(obj, force = True)
    cfg = ac.get(obj.selenium, locators, cfg_data_flow2(cfg_ks, get_co))
    nav_to(obj, True)
    return cm.map_cfg_value(cfg, False)


def reset(obj, cfg_ks):
    return set(obj, dict([(k, obj.device[k]) for k in cfg_ks]))

