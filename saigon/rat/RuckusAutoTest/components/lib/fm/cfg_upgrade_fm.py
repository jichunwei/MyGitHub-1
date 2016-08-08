from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.fm import provisioning_fm as prov
from RuckusAutoTest.components.lib.AutoConfig import \
    Ctrl, cfgDataFlow as cfg_data_flow, \
    get as ac_get, set as ac_set

Locators = copy.deepcopy(prov.DEV_SELECT_CTRLS)
Locators.update(copy.deepcopy(prov.COMMON_PROV_CTRLS))
Locators.update(dict(
    new_task_link = "//div[@id='new-task']",

    task_name = Ctrl("//input[@id='taskname']", type = 'text'),
    template_name = Ctrl("//select[@id='template']", type = 'select'),
    reboot = Ctrl("//input[@id='reboot.flag']", type = 'check'),

    save_btn = "//input[contains(@id,'-ok-ap')]",

    # re-update task detail table headers for cfg upgrade. Its headers are different
    # from fw upgrade
    task_detail_tbl = Ctrl(
        dict(tbl = "//table[@id='devicestatus']",
             nav = "//table[preceding-sibling::div[@id='tb-detail']]//td[@class='pageSelecter']",),
        type = 'ltable',
        cfg = dict(hdrs = ['name', 'serial', 'model', 'ip', 'version', 'status', 'failure', 'param']),
    ),
))

ctrl_order = prov.get_order_ctrls()
prov.PROV_TASK_TIMEOUT = 40
def nav_to(fm, force = False):
    s, l = fm.selenium, Locators
    fm.navigate_to(fm.PROVISIONING, fm.PROV_CONFIG_UPGRADE, force = force)
    # wait the page loaded
    ac_get(s, l, ['loading_ind'])

def set(obj, cfg):
    s, l, oc = obj.selenium, Locators, cfg_data_flow(cfg, ctrl_order)
    nav_to(obj, force = True)
    s.click_and_wait(l['new_task_link'])
    ac_set(s, l, cfg, oc)
    s.click_and_wait(l['save_btn'])

def get(obj, cfg_ks, is_nav = True):
    '''
    for getting Task Status Details, set is_nav=False
    '''
    s, l, oc = obj.selenium, Locators, cfg_data_flow(cfg_ks, ctrl_order)
    if is_nav:
        nav_to(obj, force = True)

    return ac_get(s, l, cfg_ks, oc)


mcfg = dict(get = get, set = set, nav_to = nav_to,) # this module config funcs

def monitor_task(obj, taskcfg, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.monitor_task(obj, taskcfg, mcfg, timeout)

def cancel_task(obj, taskcfg, timeout = prov.PROV_TASK_TIMEOUT):
    return prov.cancel_task(obj, taskcfg, mcfg, timeout)

def create_task(obj, task_name, template_name, template_model, schedule = 0, provision_to = {'device':'192.168.0.185'}):#select_by='device', ip='', group=''):
    '''
    - provision_to: it is {'device': 'ip_addr'} or {'group': 'group name'}
    '''
    cfg_task = dict(
        task_name = task_name,
        template_name = template_name + ' \(%s\)' % template_model,
        schedule = 'now' if int(schedule) == 0 else 'later',
    )
    # re-caclculate schedule time to add schedule date and time
    delta = prov.calc_schedule(cfg_task, mins = schedule)

    if provision_to.has_key('device'):
        # update cfg to provision to a device
        cfg_task.update({
            'device_tbl_click': dict(
                get = '1st',
                match = [dict(ip = provision_to['device'])],
                op = 'in',
                link = 'select',
            )
        })
    else:
        # update cfg to provision to a group
        cfg_task.update({
            'view': provision_to.get('group', '') # get group name
        })
    # create a cfg upgrade task
    set(obj, cfg_task)

    # cfg to monitor the task
    cfg_monitor = dict(
        task_name = task_name,
    )
    timeout = schedule + delta + prov.PROV_TASK_TIMEOUT
    return monitor_task(obj, cfg_monitor, timeout)

def get_task_id(obj, task_name):
    nav_to(obj, True)
    return prov.get_task_id(obj, task_name, mcfg)

def restart_task(obj, cfg = {}):
    '''
    cfg contains task_name or id or both of them.
    - cfg = {
        task_name: task name,
        id: task id
    }
    '''
    return prov.restart_task(obj, cfg, mcfg)

def is_restartable_status(ts):
    return prov.is_restartable_status(ts)

def is_success_status(ts):
    return prov.is_success_status(ts)

