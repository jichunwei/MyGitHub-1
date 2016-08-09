##################################################################################
# THIS MODULE IS TO PROVIDE UTILITY FUNCTIONS FOR FM CONFIGURE > ZONEDIRECTORS > #
# ZONEDIRECTOR CLONING                                                           #
##################################################################################
import copy
import time
from datetime import datetime

from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.fm import provisioning_fm as prov
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set


OBTAIN_CFG_TBL_HDRS = [
    'device_name', 'serial', 'internal_ip', 'external_ip', 'model', 'last_seen', 'uptime',
    'connection_status', 'tag', 'fw_version',
]

ZD_CLONE_TBL_HDRS = [
    'chk_box', 'device_name', 'serial', 'ip_addr', 'external_ip', 'model', 'created_by'
]

ZD_TASK_DETAIL_HDRS = [
    'name', 'serial', 'model', 'ip', 'version', 'status', 'failure'
]
Locators = copy.deepcopy(prov.DEV_SELECT_CTRLS)
Locators.update(copy.deepcopy(prov.COMMON_PROV_CTRLS))
Locators.update(dict(
    create_zd_cloning_task = Ctrl(loc = "//div[@id='new-task']//span", type = 'button'),
    task_name = Ctrl(loc = "//input[@id='taskname']", type = 'text'),
    cfg_type = Ctrl(
        loc = dict(
            config = "//input[@id='configtype.0']",
            restore = "//input[@id='configtype.1']"
        ),
        type = 'radioGroup',
    ),
    cfg_file_name = Ctrl(loc = "//select[@id='select-configlist']", type = 'select'),

    clone_type = Ctrl(
        loc = dict(
            full_restore = "//input[@id='type.0']",
            failover_restore = "//input[@id='type.1']",
            policy_restore = "//input[@id='type.1']",
        ),
        type = 'radioGroup',
    ),
    select_devices_tab = Ctrl(loc = "//span[contains(., 'Select Devices')]", type = 'button'),

    zd_clone_tbl = Ctrl(
        dict(
             tbl = "//table[@widgetid='ZDCloneSelectEntityTable']",
             nav = "//div[@widgetid='selectDevices']//td[contains(preceding-sibling::td, 'Number of devices')]/table"
        ),
        type = 'ltable',
        cfg = dict(
            hdrs = ZD_CLONE_TBL_HDRS,
            links = dict(
                chk_box = "//input[contains(@id, 'provisionCheckBox')]",
            ),
            get = '1st',
        ),
    ),

    save_btn = Ctrl(loc = "//input[@id='clone-ok-ap']", type = 'button'),
    cancel_btn = Ctrl(loc = "//input[@id='clone-cancel-ap']", type = 'button'),

    # Overwrite different locator for "Select View" tab
    # zd group device name
    group_name = Ctrl("//div[contains(.,'Select a view of ZoneDirector')]/span", type = 'dojo_select'),
    # The task_detail_tbl of ZD Cloning is different from Cfg Upgrade so we have
    # to overwrite it
    task_detail_tbl = Ctrl(
        dict(tbl = "//table[@id='devicestatus']",
             nav = "//table[preceding-sibling::div[@id='tb-detail']]//td[@class='pageSelecter']",),
        type = 'ltable',
        cfg = dict(hdrs = ZD_TASK_DETAIL_HDRS),
    ),
))

prov.PROV_TASK_TIMEOUT = 40

DEV_SELECT_ORDER = [
    dict(
         enter = ['create_zd_cloning_task', 'view_tab'],
         items = ['cfg_type', 'task_name', 'cfg_file_name', 'clone_type', 'group_name'],
         exit = 'save_btn',
    ),
    dict(enter = 'device_tab', items = ['device_tbl'],),
    dict(enter = 'device_tab', items = ['device_tbl_click'],),
]

COMMON_PROV_ORDER = [
    dict(enter = 'schedule', items = ['schedule_date', 'schedule_time', ],),
    dict(enter = 'refresh_btn', items = ['task_tbl'],),
    dict(enter = 'refresh_btn', items = ['task_tbl_click'],),
]
ctrl_order = prov.get_order_ctrls()

def nav_to(fm, force = False):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_ZD_CLONING, force = force)

def create_zd_cloning_task(fm, cfg = {}):
    '''
    This function is to create a ZD cloning task for a separated device or a group
    of device.
    - cfg: A dictionary of following items:
        # common cfg for cloning:
        task_name = '',
        cfg_file_name = '',
        clone_type = '',
        schedule = interval in integer,

        # specific items for doing cloning for separated devices:
        device = 'device ip',

        # specific items for doing cloning for a group of devices:
        group_name = 'group device name',

    - Return: return the timeout for this task
    '''
    s, l = fm.selenium, Locators
    nav_to(fm, True)
    _cfg = copy.deepcopy(cfg)
    order_common_ctrls = [
        'create_zd_cloning_task', 'cfg_type', 'task_name', 'cfg_file_name',
        'clone_type', 'schedule', 'schedule_date', 'schedule_time',
    ]

    # 1. Get order ctrls for "device" or "group" case
    specific_order_ctrls = []
    if _cfg.get('device', ''): # do cloning for separated "device" case
        _cfg.update({
            'device_tbl': dict(
                get = '1st',
                matches = [dict(ip = _cfg['device'])],
                op = 'in',
                link = 'select',
            )
        })
        # remove the key "device" from cfg
        del _cfg['device']
        # update order ctrls
        specific_order_ctrls = ['device_tab', 'device_tbl']
    else: # cloning for "group" of device case
        # update order ctrl for this case
        specific_order_ctrls = ['view_tab', 'group_name']

    # 2. Get the scheduled time fist. Because  "_cfg['schedule']" will be updated to
    # "now" or "later" after re-calculated by prov.calc_schedule
    schedule_interval = _cfg['schedule']

    # 3. Re-caclculate scheduled time to add schedule date and time to _cfg
    delta = prov.calc_schedule(_cfg, _cfg['schedule'], datetime.now())

    # 4. Do set config
    ac_set(s, l, _cfg, order_common_ctrls + specific_order_ctrls + ['save_btn'])
    timeout = schedule_interval + delta + prov.PROV_TASK_TIMEOUT

    # NOTE: Just return the timeout time, if re-direct this task to monitor function
    # It will cause we cannot do cancel it for cancel test case.
    # 5. Monitor the task
    # return monitor_task(fm, dict(task_name=_cfg['task_name']), timeout)
    return timeout

def get(fm, cfg_ks, is_nav = True):
    '''
    for getting Task Status Details, set is_nav=False
    '''
    s, l, oc = fm.selenium, Locators, cfg_data_flow(cfg_ks, ctrl_order)
    if is_nav:
        nav_to(fm, force = True)

    return ac_get(s, l, cfg_ks, oc)

mcfg = dict(get = get, set = create_zd_cloning_task, nav_to = nav_to,) # this module config funcs

def monitor_task(fm, taskcfg, timeout = prov.PROV_TASK_TIMEOUT):
    '''
    This function is to monitor a task.
    - taskcfg: a dictionary of match expression
        {
            'task_name': 'task name',
            'id': 'task id',
        }
    Return task status and detail when the task finished.
    '''
    return prov.monitor_task(fm, taskcfg, mcfg, timeout)

def cancel_task(fm, taskcfg, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.cancel_task(fm, taskcfg, mcfg, timeout)

def get_task_id(fm, task_name):
    nav_to(fm, True)
    return prov.get_task_id(fm, task_name, mcfg)

def restart_task(fm, cfg = {}):
    '''
    This function is to restart a zd cloning task
    - cfg: a dictionary of following items
    {
        task_name: task name,
        id: task id
    }
    '''
    return prov.restart_task(fm, cfg, mcfg)

def is_restartable_status(ts):
    return prov.is_restartable_status(ts)

def is_success_status(ts):
    return prov.is_success_status(ts)

def is_canceled_status(ts):
    return prov.is_canceled_status(ts)

def is_failed_status(ts):
    return prov.is_failed_status(ts)

def is_expired_status(ts):
    return prov.is_expired_status(ts)

